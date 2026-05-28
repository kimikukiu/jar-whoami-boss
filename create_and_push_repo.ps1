# Script pentru crearea repository-ului GitHub și push

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CREARE ȘI PUSH REPO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location D:\jarvis\ecosystem

# 1. Curățăm repository-ul existent (dacă e corupt)
Write-Host "`n1. Curățare repository existent..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue

# 2. Creăm .gitignore corect
Write-Host "`n2. Creare .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Virtual environments
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

# Large media files (exclude from git, will be separate)
*.mp4
*.avi
*.mov
*.mkv
*.mp3
*.wav
*.flac

# Images (can be included if small, exclude large ones)
*.jpg
*.jpeg
*.png
*.gif
*.bmp
*.tiff
*.webp
*.ico

# Archives
*.zip
*.tar
*.gz
*.rar
*.7z
*.bz2

# Executables and binaries
*.exe
*.dll
*.so
*.dylib
*.bin
*.app
*.msi
*.pkg
*.dmg

# Databases
*.sqlite
*.sqlite3
*.db
*.sql

# Logs
*.log
logs/
*.out

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
*.sublime-*

# Test coverage
coverage/
.coverage
htmlcov/

# Temporary files
tmp/
temp/
*.tmp
*.temp
.cache/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
video_analysis/
transcriptions/
frames_*/
temp_audio/
*.analysis.json
*.transcription.json
"@

$gitignoreContent | Out-File -FilePath .gitignore -Encoding UTF8 -Force
Write-Host "   ✓ .gitignore creat cu succes" -ForegroundColor Green

# 3. Inițializare git
Write-Host "`n3. Inițializare repository git..." -ForegroundColor Yellow
git init

# 4. Adăugare fisiere (exclude node_modules și fisiere mari)
Write-Host "`n4. Adăugare fișiere..." -ForegroundColor Yellow
git add .

# 5. Commit
Write-Host "`n5. Creare commit..." -ForegroundColor Yellow
git commit -m "Initial JARVIS commit - Supreme Commander Architecture

- Agent system with autonomous execution
- Video analysis and UI replication  
- Multi-ecosystem deployment
- JARVIS Core v2.0
- Complete Python backend with async support
- React frontend with 3D visualization
- Voice control with Whisper STT
- Social media, code generation, automation modules"

# 6. Creare branch main
git branch -M main

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " REPOSITORY PREGĂTIT LOCAL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pentru a finaliza push-ul pe GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Creează repository pe GitHub:" -ForegroundColor Cyan
Write-Host "   https://github.com/new" -ForegroundColor White
Write-Host "   Nume: jar-whoami-boss" -ForegroundColor White
Write-Host "   Vizibilitate: Public sau Private" -ForegroundColor White
Write-Host ""
Write-Host "2. Rulează în terminal:" -ForegroundColor Cyan
Write-Host "   git remote add origin https://github.com/USERNAME/jar-whoami-boss.git" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "   Sau autentifică-te cu token:" -ForegroundColor Cyan
Write-Host "   git remote add origin https://TOKEN@github.com/USERNAME/jar-whoami-boss.git" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green

pause
