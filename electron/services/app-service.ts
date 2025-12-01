import { BaseService } from './base-service';
import { app, dialog } from 'electron';
import * as fs from 'fs';
import * as path from 'path';

export class AppService extends BaseService {

  async getVersion(): Promise<string> {
    try {
      return app.getVersion();
    } catch (error) {
      this.handleError(error, 'Get app version');
    }
  }

  async exportData(): Promise<string> {
    try {
      const exportData = {
        metadata: {
          exportDate: new Date().toISOString(),
          version: '1.0.0',
          appVersion: app.getVersion()
        },
        teams: this.daoManager.teams.getAll(),
        seasons: this.daoManager.seasons.getAll(),
        // Note: Games are exported with their seasons
        settings: await this.getAllAppSettings()
      };

      return JSON.stringify(exportData, null, 2);
    } catch (error) {
      this.handleError(error, 'Export data');
    }
  }

  async importData(jsonData: string): Promise<void> {
    try {
      const data = JSON.parse(jsonData);
      
      this.daoManager.transaction((dao) => {
        // Import seasons (teams are read-only in this implementation)
        if (data.seasons) {
          for (const season of data.seasons) {
            dao.seasons.create({
              name: season.name,
              year: season.year,
              status: season.status,
              current_week: season.current_week
            });
          }
        }
        
        // Import settings
        if (data.settings) {
          for (const [key, value] of Object.entries(data.settings)) {
            this.setAppSetting(key, value as string);
          }
        }
      });
    } catch (error) {
      this.handleError(error, 'Import data');
    }
  }

  async showSaveDialog(options: any): Promise<any> {
    try {
      const result = await dialog.showSaveDialog(options);
      return result;
    } catch (error) {
      this.handleError(error, 'Show save dialog');
    }
  }

  async showOpenDialog(options: any): Promise<any> {
    try {
      const result = await dialog.showOpenDialog(options);
      return result;
    } catch (error) {
      this.handleError(error, 'Show open dialog');
    }
  }

  async createBackup(name?: string): Promise<string> {
    try {
      const userDataPath = app.getPath('userData');
      const backupsDir = path.join(userDataPath, 'backups');
      
      // Ensure backups directory exists
      if (!fs.existsSync(backupsDir)) {
        fs.mkdirSync(backupsDir, { recursive: true });
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupName = name || `backup-${timestamp}`;
      const backupPath = path.join(backupsDir, `${backupName}.db`);
      
      // Get current database path
      const dbPath = this.getDatabasePath();
      
      // Copy database file
      fs.copyFileSync(dbPath, backupPath);
      
      // Create metadata file
      const metadataPath = path.join(backupsDir, `${backupName}.json`);
      const metadata = {
        name: backupName,
        created: new Date().toISOString(),
        appVersion: app.getVersion(),
        size: fs.statSync(backupPath).size
      };
      fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
      
      // Clean up old backups (keep last 10)
      await this.cleanupOldBackups(backupsDir);
      
      return backupPath;
    } catch (error) {
      this.handleError(error, 'Create backup');
    }
  }

  async restoreBackup(backupName: string): Promise<void> {
    try {
      const userDataPath = app.getPath('userData');
      const backupPath = path.join(userDataPath, 'backups', `${backupName}.db`);
      
      if (!fs.existsSync(backupPath)) {
        throw new Error(`Backup ${backupName} not found`);
      }
      
      const dbPath = this.getDatabasePath();
      
      // Copy backup to current database location
      fs.copyFileSync(backupPath, dbPath);
    } catch (error) {
      this.handleError(error, 'Restore backup');
    }
  }

  async listBackups(): Promise<any[]> {
    try {
      const userDataPath = app.getPath('userData');
      const backupsDir = path.join(userDataPath, 'backups');
      
      if (!fs.existsSync(backupsDir)) {
        return [];
      }
      
      const files = fs.readdirSync(backupsDir);
      const metadataFiles = files.filter(f => f.endsWith('.json'));
      
      const backups = [];
      for (const file of metadataFiles) {
        try {
          const metadataPath = path.join(backupsDir, file);
          const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
          backups.push(metadata);
        } catch (error) {
          console.warn(`Failed to read backup metadata: ${file}`);
        }
      }
      
      return backups.sort((a, b) => new Date(b.created).getTime() - new Date(a.created).getTime());
    } catch (error) {
      this.handleError(error, 'List backups');
    }
  }

  async deleteBackup(backupName: string): Promise<void> {
    try {
      const userDataPath = app.getPath('userData');
      const backupsDir = path.join(userDataPath, 'backups');
      
      const backupPath = path.join(backupsDir, `${backupName}.db`);
      const metadataPath = path.join(backupsDir, `${backupName}.json`);
      
      if (fs.existsSync(backupPath)) {
        fs.unlinkSync(backupPath);
      }
      
      if (fs.existsSync(metadataPath)) {
        fs.unlinkSync(metadataPath);
      }
    } catch (error) {
      this.handleError(error, 'Delete backup');
    }
  }

  private async getAllAppSettings(): Promise<Record<string, string>> {
    const settings: Record<string, string> = {};
    
    try {
      // Get all settings from the database
      const rows = this.daoManager.teams.executeQuery('SELECT key, value FROM app_settings');
      for (const row of rows) {
        settings[row.key] = row.value;
      }
    } catch (error) {
      // Settings table might not exist yet, return empty object
      console.warn('Could not load app settings:', error);
    }
    
    return settings;
  }

  private setAppSetting(key: string, value: string): void {
    try {
      this.daoManager.teams.executeUpdate(`
        INSERT OR REPLACE INTO app_settings (key, value, updated_at) 
        VALUES (?, ?, ?)
      `, [key, value, new Date().toISOString()]);
    } catch (error) {
      console.warn('Could not save app setting:', error);
    }
  }

  private getDatabasePath(): string {
    const userDataPath = app.getPath('userData');
    return path.join(userDataPath, 'app-data.db');
  }

  private async cleanupOldBackups(backupsDir: string): Promise<void> {
    try {
      const maxBackups = 10;
      const backups = await this.listBackups();
      
      if (backups.length > maxBackups) {
        const toDelete = backups.slice(maxBackups);
        
        for (const backup of toDelete) {
          await this.deleteBackup(backup.name);
        }
      }
    } catch (error) {
      console.warn('Failed to cleanup old backups:', error);
    }
  }

  async getDatabaseStats(): Promise<any> {
    try {
      return this.daoManager.getDatabaseStats();
    } catch (error) {
      this.handleError(error, 'Get database stats');
    }
  }

  async performHealthCheck(): Promise<any> {
    try {
      return this.daoManager.performHealthCheck();
    } catch (error) {
      this.handleError(error, 'Perform health check');
    }
  }
}