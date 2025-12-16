import { app, BrowserWindow, ipcMain, shell } from 'electron';
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
  private loadRetryCount: number = 0;
  private maxLoadRetries: number = 3;
  private retryDelay: number = 2000; // 2 seconds

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
    
    setupIpcHandlers(this.daoManager, this.dbManager || undefined);
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
        preload: path.join(__dirname, 'preload.js'),
        sandbox: false // Disable sandbox for development
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
      const devPort = process.env.VITE_DEV_SERVER_PORT || '5173';
      this.loadDevServer(devPort);
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

    // Handle dev server connection errors
    if (!app.isPackaged) {
      this.setupDevServerErrorHandling();
    }
  }

  private async loadDevServer(port: string): Promise<void> {
    const url = `http://localhost:${port}`;
    
    try {
      await this.mainWindow?.loadURL(url);
      this.loadRetryCount = 0; // Reset on successful load
      this.mainWindow?.webContents.openDevTools();
    } catch (error) {
      console.error(`❌ Failed to load dev server at ${url}:`, error);
      this.handleDevServerError(port);
    }
  }

  private setupDevServerErrorHandling(): void {
    if (!this.mainWindow) return;

    // Handle navigation errors (e.g., server not available)
    this.mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
      // Ignore aborted loads (-3) as these are intentional cancellations
      if (errorCode === -3) return;
      
      console.error(`❌ Failed to load page: ${errorDescription} (${errorCode})`);
      console.error(`   URL: ${validatedURL}`);
      
      const port = process.env.VITE_DEV_SERVER_PORT || '5173';
      this.handleDevServerError(port);
    });

    // Handle render process crashes
    this.mainWindow.webContents.on('render-process-gone', (event, details) => {
      console.error('❌ Renderer process crashed:', details);
      
      if (details.reason !== 'clean-exit') {
        this.showErrorDialog('Renderer process crashed', 'The application will now close.');
        app.quit();
      }
    });
  }

  private handleDevServerError(port: string): void {
    if (this.loadRetryCount < this.maxLoadRetries) {
      this.loadRetryCount++;
      console.log(`🔄 Retrying dev server connection (${this.loadRetryCount}/${this.maxLoadRetries})...`);
      
      setTimeout(() => {
        this.loadDevServer(port);
      }, this.retryDelay);
    } else {
      console.error('❌ Max retries reached. Dev server appears to be down.');
      this.showDevServerErrorPage();
    }
  }

  private showDevServerErrorPage(): void {
    if (!this.mainWindow) return;

    const errorHtml = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <title>Dev Server Connection Error</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100vh;
              margin: 0;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
            }
            .container {
              text-align: center;
              max-width: 600px;
              padding: 40px;
              background: rgba(255, 255, 255, 0.1);
              border-radius: 20px;
              backdrop-filter: blur(10px);
              box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
              font-size: 48px;
              margin: 0 0 20px 0;
            }
            p {
              font-size: 18px;
              line-height: 1.6;
              margin: 20px 0;
            }
            .error-icon {
              font-size: 80px;
              margin-bottom: 20px;
            }
            button {
              background: white;
              color: #667eea;
              border: none;
              padding: 12px 30px;
              font-size: 16px;
              font-weight: 600;
              border-radius: 8px;
              cursor: pointer;
              margin: 10px;
              transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            .code {
              background: rgba(0, 0, 0, 0.3);
              padding: 10px 15px;
              border-radius: 8px;
              font-family: 'Courier New', monospace;
              font-size: 14px;
              margin: 20px 0;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="error-icon">⚠️</div>
            <h1>Dev Server Not Available</h1>
            <p>Unable to connect to the Vite development server.</p>
            <div class="code">npm run dev:renderer</div>
            <p>Please ensure the dev server is running on port ${process.env.VITE_DEV_SERVER_PORT || '5173'}, then click retry.</p>
            <button onclick="window.location.reload()">🔄 Retry Connection</button>
            <button onclick="require('electron').ipcRenderer.send('quit-app')">❌ Close Application</button>
          </div>
        </body>
      </html>
    `;

    this.mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`);
  }

  private showErrorDialog(title: string, message: string): void {
    const { dialog } = require('electron');
    dialog.showErrorBox(title, message);
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
  contents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
});

// Export for testing
export { FootballSimApp };