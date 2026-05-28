@echo off
REM Script pentru push pe GitHub

cd /d D:\jarvis\ecosystem

echo Initializare repository...
git init

echo Adaugare fisiere...
git add .

echo Commit...
git commit -m "Initial JARVIS commit - Supreme Commander Architecture"

echo Adaugare remote...
git remote add origin https://github.com/jarvis-ai/jar-whoami-boss.git 2>nul

echo Push...
git push -u origin main --force

echo Gata!
pause
