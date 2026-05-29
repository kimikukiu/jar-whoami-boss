@echo off
REM JARVIS 24/7 Builder - Creates Windows Executable
REM Run this script to build JARVIS.exe

echo ====================================
echo JARVIS 24/7 EXE Builder
echo ====================================

cd /d "%~dp0"

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Create spec file
echo Creating JARVIS.spec...

(
echo # -*- mode: python ; coding: utf-8 -*-
echo a = Analysis(
echo     ['jarvis_24_7.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=[
echo         'edge_tts',
echo         'whisper',
echo         'speech_recognition',
echo         'pygame',
echo         'numpy',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     noarchive=False,
echo     optimize=0,
echo )
echo
echo pyz = PYZ(a.pure)
echo
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.datas,
echo     [],
echo     name='JARVIS_24_7',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon='icon.ico',
echo     version='version.txt',
echo )
) > JARVIS.spec

REM Check for icon
if not exist "icon.ico" (
    echo Icon not found, using default...
)

REM Build the executable
echo.
echo Building JARVIS.exe...
echo This may take a few minutes...
echo.

pyinstaller JARVIS.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    pause
    exit /b 1
)

echo.
echo ====================================
echo BUILD SUCCESSFUL!
echo ====================================
echo.
echo Executable location:
echo   dist\JARVIS_24_7.exe
echo.
echo To run:
echo   dist\JARVIS_24_7.exe
echo.
pause
