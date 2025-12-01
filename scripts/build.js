const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

async function build() {
  console.log('🏗️  Building Football Simulation Electron App...\n');

  try {
    // 1. Clean previous builds
    console.log('🧹 Cleaning previous builds...');
    await fs.remove('dist');
    await fs.remove('dist-electron');
    
    // 2. Build renderer (React frontend)
    console.log('⚛️  Building renderer process...');
    execSync('npx vite build --config vite.config.electron.ts', { stdio: 'inherit' });
    
    // 3. Build main process (Electron backend)
    console.log('🔧 Building main process...');
    execSync('npx tsc -p tsconfig.electron.json', { stdio: 'inherit' });
    
    // 4. Copy package.json to dist-electron
    console.log('📦 Copying package.json...');
    const packageJson = await fs.readJson('package.json');
    const electronPackageJson = {
      name: packageJson.name,
      version: packageJson.version,
      description: packageJson.description,
      main: 'main.js',
      author: packageJson.author,
      license: packageJson.license,
      dependencies: {
        'better-sqlite3': packageJson.dependencies['better-sqlite3']
      }
    };
    await fs.writeJson('dist-electron/package.json', electronPackageJson, { spaces: 2 });
    
    console.log('✅ Build completed successfully!');
    console.log('\nTo run the app: npm run electron dist-electron/main.js');
    
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

build();