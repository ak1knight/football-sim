const { spawn, exec } = require('child_process');
const chokidar = require('chokidar');
const path = require('path');

let electronProcess = null;
let rendererServer = null;
let manualRestart = false;

let vitePort = '5173';

async function startRenderer() {
  console.log('🚀 Starting Vite dev server...');
  
  return new Promise((resolve, reject) => {
    const viteProcess = spawn('npx', ['vite', '--config', 'vite.config.electron.ts', '--port', '5173'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    viteProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Vite] ${output.trim()}`);
      
      // Extract port from Vite output
      const portMatch = output.match(/Local:\s+http:\/\/localhost:(\d+)/);
      if (portMatch) {
        vitePort = portMatch[1];
        process.env.VITE_DEV_SERVER_PORT = vitePort;
        console.log(`✅ Vite dev server started on port ${vitePort}`);
        resolve(viteProcess);
      } else if (output.includes('ready in')) {
        console.log('✅ Vite dev server started');
        resolve(viteProcess);
      }
    });

    viteProcess.stderr.on('data', (data) => {
      console.error(`[Vite Error] ${data.toString().trim()}`);
    });

    viteProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Vite process exited with code ${code}`));
      }
    });

    rendererServer = viteProcess;
  });
}

function buildElectron() {
  console.log('🔧 Building Electron main process...');
  
  return new Promise((resolve, reject) => {
    exec('npx tsc -p tsconfig.electron.json', (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ TypeScript build failed:`, error);
        reject(error);
        return;
      }
      
      if (stderr) {
        console.warn(`[TypeScript] ${stderr.trim()}`);
      }
      
      if (stdout) {
        console.log(`[TypeScript] ${stdout.trim()}`);
      }
      
      console.log('✅ Electron main process built');
      resolve();
    });
  });
}

function startElectron() {
  if (electronProcess) {
    return;
  }

  console.log('⚡ Starting Electron...');
  
  const electronPath = require('electron');
  const args = [
    '--inspect=9229',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    path.join(__dirname, '../dist-electron/electron/main.js')
  ];

  electronProcess = spawn(electronPath, args, {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, VITE_DEV_SERVER_PORT: vitePort }
  });
  
  electronProcess.stdout.on('data', (data) => {
    console.log(`[Electron] ${data.toString().trim()}`);
  });
  
  electronProcess.stderr.on('data', (data) => {
    console.log(`[Electron] ${data.toString().trim()}`);
  });
  
  electronProcess.on('close', (code) => {
    console.log(`📫 Electron process exited with code ${code}`);
    if (!manualRestart) {
      process.exit(code);
    }
    electronProcess = null;
  });
  
  console.log('✅ Electron started');
}

async function restartElectron() {
  if (electronProcess) {
    console.log('🔄 Restarting Electron...');
    manualRestart = true;
    electronProcess.kill();
    electronProcess = null;
    manualRestart = false;
    
    // Wait a moment before restarting
    setTimeout(() => {
      startElectron();
    }, 1000);
  }
}

function watchElectronFiles() {
  console.log('👀 Watching Electron files for changes...');
  
  const watcher = chokidar.watch('electron/**/*', {
    ignored: /node_modules/,
    persistent: true
  });
  
  let buildTimeout = null;
  
  watcher.on('change', (filePath) => {
    console.log(`📝 File changed: ${filePath}`);
    
    // Debounce builds
    if (buildTimeout) {
      clearTimeout(buildTimeout);
    }
    
    buildTimeout = setTimeout(async () => {
      try {
        await buildElectron();
        await restartElectron();
      } catch (error) {
        console.error('Failed to rebuild/restart:', error);
      }
    }, 500);
  });
  
  return watcher;
}

async function cleanup() {
  console.log('🧹 Cleaning up processes...');
  
  if (electronProcess) {
    electronProcess.kill();
  }
  
  if (rendererServer) {
    rendererServer.kill();
  }
  
  process.exit(0);
}

async function startDev() {
  console.log('🚀 Starting Football Simulation development environment...\n');
  
  try {
    // Build Electron main process first
    await buildElectron();
    
    // Start Vite dev server
    await startRenderer();
    
    // Wait a moment for the server to be fully ready
    setTimeout(() => {
      // Start Electron
      startElectron();
      
      // Set up file watching
      watchElectronFiles();
    }, 2000);
    
    // Handle graceful shutdown
    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
    process.on('exit', cleanup);
    
  } catch (error) {
    console.error('❌ Failed to start development environment:', error);
    process.exit(1);
  }
}

// Start the development environment
startDev();