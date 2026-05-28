@echo off
title JARVIS - GitHub Sync
color 0A
cd /d d:\jarvis\ecosystem
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║     JARVIS ECOSYSTEM - GITHUB SYNC                          ║
echo  ║     Pushing to: kimikukiu                                    ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo Backing up Ollama models...
python -c "from tools.auto_start import get_auto_start; import asyncio; asyncio.run(get_auto_start().backup_ollama_models())"
echo.
echo Syncing to GitHub...
python -c "from tools.auto_start import get_auto_start; import asyncio; asyncio.run(get_auto_start().push_to_github())"
echo.
echo Sync complete!
pause