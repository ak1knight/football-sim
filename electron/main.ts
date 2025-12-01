import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { DatabaseManager } from './database/database-manager';
import { DAOManager } from './database/dao/dao-manager';
import { setupIpcHandlers } from './ipc/ipc-main';
import { AutoUpdater } from './auto-updater';

class FootballSimApp {
  private mainWindow: BrowserWindow | null = null;
  private dbManager: DatabaseManager | null = null;
  private daoManager: DAOManager | null = null;
  private autoUpdater: AutoUpdater | null = null;

  async initialize(): Promise<void> {
    console.log('🚀 Initializing Football Simulation Engine...');
    
    await this.setupDatabase();
    await this.setupIpc();
    this.createMainWindow();
    
    if (!app.isPackaged) {
      console.log('📝 Development mode - Auto-updater disabled');
    } else {
      this.setupAutoUpdater();
    }
    
    console.log('✅ Application initialized successfully');
  }

  private async setupDatabase(): Promise<void> {
    console.log('🗄️  Setting up database...');
    
    try {
      this.dbManager = new DatabaseManager();
      await this.dbManager.initialize();
      await this.dbManager.runMigrations();
      await this.dbManager.seedInitialData();
      
      this.daoManager = new DAOManager(this.dbManager.getDatabase());
      
      console.log('✅ Database setup complete');
    } catch (error) {
      console.error('❌ Database setup failed:', error);
      throw error;
    }
  }

  private async setupIpc(): Promise<void> {
    console.log('🔗 Setting up IPC handlers...');
    
    if (!this.daoManager) {
      throw new Error('Database must be initialized before IPC setup');
    }
    
    setupIpcHandlers(this.daoManager);
    console.log('✅ IPC handlers registered');
  }

  private createMainWindow(): void {
    console.log('🪟 Creating main window...');
    
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      icon: path.join(__dirname, '../assets/icons/icon.png'),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
      },
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      show: false, // Don't show until ready
    });

    // Load the renderer
    if (app.isPackaged) {
      // Production: load built files
      this.mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    } else {
      // Development: load from Vite dev server
      this.mainWindow.loadURL('http://localhost:5173');
      this.mainWindow.webContents.openDevTools();
    }

    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
      console.log('✅ Main window displayed');
    });

    // Handle window closed
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      // Open external links in default browser
      if (url.startsWith('http') || url.startsWith('https')) {
        require('electron').shell.openExternal(url);
        return { action: 'deny' };
      }
      return { action: 'allow' };
    });
  }

  private setupAutoUpdater(): void {
    if (this.mainWindow) {
      this.autoUpdater = new AutoUpdater(this.mainWindow);
    }
  }

  getMainWindow(): BrowserWindow | null {
    return this.mainWindow;
  }

  async cleanup(): Promise<void> {
    console.log('🧹 Cleaning up application...');
    
    if (this.dbManager) {
      await this.dbManager.close();
    }
    
    console.log('✅ Cleanup complete');
  }
}

// Application instance
const footballSimApp = new FootballSimApp();

// App event handlers
app.whenReady().then(async () => {
  try {
    await footballSimApp.initialize();
  } catch (error) {
    console.error('Failed to initialize application:', error);
    app.quit();
  }

  // macOS: Re-create window when dock icon clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      footballSimApp.initialize();
    }
  });
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle app quit
app.on('before-quit', async () => {
  await footballSimApp.cleanup();
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (navigationEvent, navigationURL) => {
    navigationEvent.preventDefault();
  });
});

// Export for testing
export { FootballSimApp };