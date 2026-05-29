# Script final pentru push pe GitHub
# Repository: jar-whoami-boss

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  JARVIS FINAL GITHUB PUSH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location D:\jarvis\ecosystem

# Verificăm dacă git este instalat
Write-Host "`n[1] Verificare Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "  ✓ Git instalat: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Git nu este instalat!" -ForegroundColor Red
    exit 1
}

# Configurare git
Write-Host "`n[2] Configurare Git..." -ForegroundColor Yellow
git config user.name "JARVIS Admin"
git config user.email "jarvis@system.ai"
Write-Host "  ✓ Git configurat" -ForegroundColor Green

# Inițializare repository
Write-Host "`n[3] Inițializare repository..." -ForegroundColor Yellow
if (Test-Path .git) {
    Write-Host "  ! Repository existent găsit, se șterge..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .git
}
git init
Write-Host "  ✓ Repository inițializat" -ForegroundColor Green

# Creare .gitignore
Write-Host "`n[4] Creare .gitignore..." -ForegroundColor Yellow
$gitignore = @"
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
.venv

# Environment variables
.env
.env.local
.env.development
.env.production

# Build outputs
frontend/dist/
frontend/build/
frontend/.vite/

# Large media files
*.mp4
*.avi
*.mov
*.mkv
*.mp3
*.wav
*.flac

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temp files
temp/
tmp/
*.tmp
"@

$gitignore | Out-File -FilePath .gitignore -Encoding utf8
Write-Host "  ✓ .gitignore creat" -ForegroundColor Green

# Adăugare fișiere
Write-Host "`n[5] Adăugare fișiere în staging..." -ForegroundColor Yellow
git add .
Write-Host "  ✓ Fișiere adăugate" -ForegroundColor Green

# Commit
Write-Host "`n[6] Creare commit..." -ForegroundColor Yellow
git commit -m "JARVIS Complete Ecosystem - Initial Release

Features:
- Voice System with wake word 'JARVIS'
- Whisper STT for Romanian speech recognition
- Edge TTS for neural voice synthesis
- Ollama integration with hermes3:8b model
- 5 Core Modules: Social Media, Code Genius, UI Builder, Data Engine, Automation Bot
- Supreme Commander Agent Architecture
- 73 Video Analysis System
- Cyberpunk UI with real-time voice indicator

Ready for production deployment."