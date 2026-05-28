# PowerShell script pentru push pe GitHub

Set-Location D:\jarvis\ecosystem

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PUSH JARVIS TO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Initializeaza repo daca nu exista
git init

# Adauga fisierele importante (excludem node_modules si fisierele mari)
Write-Host "`nAdaugare fisiere..." -ForegroundColor Yellow
git add README.md 2>$null
git add *.py 2>$null
git add *.bat 2>$null
git add *.ps1 2>$null
git add requirements.txt 2>$null
git add .gitignore 2>$null

# Creaza .gitignore daca nu exista
if (!(Test-Path .gitignore)) {
    @"
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
frontend/node_modules/
frontend/dist/
frontend/build/
*.mp4
*.avi
*.mov
*.mkv
*.mp3
*.wav
*.jpg
*.jpeg
*.png
*.gif
*.ico
*.zip
*.tar
*.gz
*.rar
*.7z
*.exe
*.dll
*.so
*.dylib
*.bin
*.dat
*.log
*.sqlite
*.db
.DS_Store
Thumbs.db
"@ | Out-File -FilePath .gitignore -Encoding UTF8
    Write-Host "Creat .gitignore" -ForegroundColor Green
}

# Status
git status

# Commit
Write-Host "`nCreare commit..." -ForegroundColor Yellow
git commit -m "Initial JARVIS commit - Supreme Commander Architecture`n`n- Agent system with autonomous execution`n- Video analysis and UI replication`n- Multi-ecosystem deployment`n- JARVIS Core v2.0" 2>$null

# Adauga remote
git remote remove origin 2>$null
git remote add origin https://github.com/jarvis-ai/jar-whoami-boss.git 2>$null

# Push
Write-Host "`nPush pe GitHub..." -ForegroundColor Yellow
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host " SUCCES! Repository-ul a fost pusat!" -ForegroundColor Green
    Write-Host " https://github.com/jarvis-ai/jar-whoami-boss" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host " EROARE! Push-ul a esuat!" -ForegroundColor Red
    Write-Host " Verificati credentialele GitHub" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Red
}

pause
