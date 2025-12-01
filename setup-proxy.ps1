# PowerShell script to configure environment for Zscaler corporate proxy
# Run this before npm install or npm run commands

Write-Host "🔧 Configuring environment for Zscaler corporate proxy..." -ForegroundColor Green

# Set environment variables for Node.js and npm to work with corporate proxy
$env:NODE_TLS_REJECT_UNAUTHORIZED="0"
$env:ELECTRON_GET_USE_PROXY="true"
$env:GLOBAL_AGENT_FORCE_GLOBAL_AGENT="false"

# Configure npm settings
npm config set strict-ssl false
npm config set registry https://registry.npmjs.org/

Write-Host "✅ Environment configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Useful commands for Zscaler environment:" -ForegroundColor Yellow
Write-Host "  npm install                    # Install dependencies" -ForegroundColor White
Write-Host "  npm run rebuild                # Rebuild native modules for Electron" -ForegroundColor White  
Write-Host "  npm run dev                    # Start development environment" -ForegroundColor White
Write-Host ""
Write-Host "Note: This disables TLS verification for development only." -ForegroundColor Red
Write-Host "Environment variables are set for this PowerShell session only." -ForegroundColor Yellow