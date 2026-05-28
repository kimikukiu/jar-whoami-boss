@echo off
title JARVIS Ecosystem - Autonomous AI Agent Network
color 0A
cd /d d:\jarvis\ecosystem

set AUTO_MODE=0
if /I "%~1"=="--auto" set AUTO_MODE=1

set INSTALL_LANG=0
if /I "%~1"=="--install-lang" set INSTALL_LANG=1

echo.
echo Installing Romanian Speech / TTS (ro-RO) if missing...
if %INSTALL_LANG%==1 (
  net session >nul 2>&1
  if %errorlevel% neq 0 (
    echo ERROR: Not running as admin. Close and re-run as Administrator.
    exit /b 1
  )
  echo Writing install log to d:\jarvis\ecosystem\lang_install.log
  powershell -NoProfile -Command "$ErrorActionPreference='Continue'; try { $null = Add-WindowsCapability -Online -Name 'Language.Basic~~~ro-RO~0.0.1.0'; $null = Add-WindowsCapability -Online -Name 'Language.Speech~~~ro-RO~0.0.1.0'; $null = Add-WindowsCapability -Online -Name 'Language.TextToSpeech~~~ro-RO~0.0.1.0'; 'OK' } catch { $_.Exception.Message; exit 2 }" > d:\jarvis\ecosystem\lang_install.log 2>&1
  echo Done installing language capabilities.
  exit /b 0
)
if %AUTO_MODE%==0 (
  if %INSTALL_LANG%==0 (
    net session >nul 2>&1
    if %errorlevel% neq 0 (
      echo Requesting Administrator privileges (one-time) to install ro-RO speech...
      powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList '--install-lang'"
      exit /b
    )
  )
)

if %AUTO_MODE%==1 (
  echo Auto mode: skipping language install.
) else (
  net session >nul 2>&1
  if %errorlevel% equ 0 (
    powershell -NoProfile -Command "Try { Add-WindowsCapability -Online -Name 'Language.Basic~~~ro-RO~0.0.1.0' -ErrorAction SilentlyContinue ^| Out-Null; Add-WindowsCapability -Online -Name 'Language.Speech~~~ro-RO~0.0.1.0' -ErrorAction SilentlyContinue ^| Out-Null; Add-WindowsCapability -Online -Name 'Language.TextToSpeech~~~ro-RO~0.0.1.0' -ErrorAction SilentlyContinue ^| Out-Null } Catch { }"
  ) else (
    echo Not running as admin. Skipping language install.
  )
)
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║     JARVIS ECOSYSTEM - AUTO START                           ║
echo  ║     Created by: WHOAMISec AGLegends                          ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo Freeing ports (8000, 3301) if already in use...
for %%P in (8000 3301) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
  )
)
echo.
echo Starting JARVIS Backend (API on 8000)...
powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -FilePath cmd.exe -ArgumentList '/c','cd /d d:\jarvis\ecosystem && python main.py'"
echo.
echo Starting JARVIS UI (fixed port 3301)...
powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -FilePath cmd.exe -ArgumentList '/c','cd /d d:\jarvis\ecosystem\frontend && npm run dev -- --port 3301 --strictPort'"
echo.
echo Opening JARVIS as Desktop App (Edge app-mode)...
echo Waiting for UI to be ready...
for /L %%I in (1,1,30) do (
  powershell -NoProfile -Command "if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 3301).TcpTestSucceeded) { exit 0 } else { exit 1 }" >nul 2>&1
  if %errorlevel%==0 goto :OPEN_APP
  timeout /t 1 /nobreak > nul
)
:OPEN_APP
set EDGE_EXE=
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set EDGE_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set EDGE_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe

if not "%EDGE_EXE%"=="" (
  start "" "%EDGE_EXE%" --app="http://localhost:3301/" --new-window --start-fullscreen
) else (
  start "" "http://localhost:3301/"
)
echo.
echo JARVIS launched. You can close this window.
pause > nul
