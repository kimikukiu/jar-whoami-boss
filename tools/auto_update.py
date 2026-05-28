"""
JARVIS Auto-Update System
Self-updating capabilities
"""

import asyncio
import subprocess
import os
from typing import Dict, Any
from datetime import datetime


class AutoUpdateSystem:
    """
    JARVIS Self-Update System
    Can update itself, install dependencies, rebuild, and restart
    """

    def __init__(self, jarvis_path: str = None):
        self.jarvis_path = jarvis_path or os.path.dirname(os.path.abspath(__file__))
        self.last_update = None
        self.update_history = []

    async def check_for_updates(self) -> Dict[str, Any]:
        """Check if updates are available"""
        try:
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.jarvis_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            result = subprocess.run(
                ["git", "status"],
                cwd=self.jarvis_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            behind = "behind" in result.stdout.lower()

            return {
                "status": "checked",
                "behind": behind,
                "current_branch": self._get_branch(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def update(self, mode: str = "full") -> Dict[str, Any]:
        """Perform self-update"""
        update_log = {
            "started_at": datetime.now().isoformat(),
            "mode": mode,
            "steps": []
        }

        try:
            if mode in ["full", "code"]:
                step = await self._update_code()
                update_log["steps"].append(step)

            if mode in ["full", "deps"]:
                step = await self._update_dependencies()
                update_log["steps"].append(step)

            if mode in ["full", "build"]:
                step = await self._rebuild()
                update_log["steps"].append(step)

            update_log["status"] = "success"
            update_log["completed_at"] = datetime.now().isoformat()
            self.last_update = datetime.now()
            self.update_history.append(update_log)

            return update_log

        except Exception as e:
            update_log["status"] = "failed"
            update_log["error"] = str(e)
            return update_log

    async def _update_code(self) -> Dict[str, Any]:
        """Pull latest code from git"""
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.jarvis_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "step": "code_update",
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"step": "code_update", "status": "error", "message": str(e)}

    async def _update_dependencies(self) -> Dict[str, Any]:
        """Update Python and npm dependencies"""
        results = []

        try:
            result_py = subprocess.run(
                ["pip", "install", "-r", "requirements.txt", "--upgrade"],
                cwd=self.jarvis_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            results.append({"type": "python", "status": "success" if result_py.returncode == 0 else "failed"})
        except Exception as e:
            results.append({"type": "python", "status": "error", "message": str(e)})

        try:
            result_npm = subprocess.run(
                ["npm", "install"],
                cwd=os.path.join(self.jarvis_path, "frontend"),
                capture_output=True,
                text=True,
                timeout=120
            )
            results.append({"type": "npm", "status": "success" if result_npm.returncode == 0 else "failed"})
        except Exception as e:
            results.append({"type": "npm", "status": "error", "message": str(e)})

        return {"step": "dependencies", "results": results}

    async def _rebuild(self) -> Dict[str, Any]:
        """Rebuild the system"""
        results = []

        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=os.path.join(self.jarvis_path, "frontend"),
                capture_output=True,
                text=True,
                timeout=180
            )
            results.append({"type": "frontend", "status": "success" if result.returncode == 0 else "failed"})
        except Exception as e:
            results.append({"type": "frontend", "status": "error", "message": str(e)})

        return {"step": "build", "results": results}

    async def restart(self) -> Dict[str, Any]:
        """Restart JARVIS"""
        return {
            "status": "restart_initiated",
            "message": "JARVIS will restart in 5 seconds",
            "command": "python main.py"
        }

    async def rollback(self, version: str = "previous") -> Dict[str, Any]:
        """Rollback to previous version"""
        try:
            result = subprocess.run(
                ["git", "reset", "--hard", f"HEAD~1" if version == "previous" else version],
                cwd=self.jarvis_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "status": "rolled_back",
                "version": version,
                "output": result.stdout
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.jarvis_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def get_update_history(self) -> list:
        """Get update history"""
        return self.update_history

    async def install_new_capability(self, capability: str) -> Dict[str, Any]:
        """Install new capability/agent"""
        capabilities = {
            "voice": "pip install SpeechRecognition pyttsx3",
            "vision": "pip install opencv-python pillow",
            "browser": "pip install selenium playwright",
            "database": "pip install psycopg2 sqlalchemy",
        }

        if capability.lower() not in capabilities:
            return {"status": "unknown_capability", "available": list(capabilities.keys())}

        try:
            cmd = capabilities[capability.lower()]
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=120
            )

            return {
                "status": "installed" if result.returncode == 0 else "failed",
                "capability": capability,
                "output": result.stdout
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


_auto_update: AutoUpdateSystem = None


def get_auto_update(jarvis_path: str = None) -> AutoUpdateSystem:
    """Get auto-update singleton"""
    global _auto_update
    if _auto_update is None:
        _auto_update = AutoUpdateSystem(jarvis_path)
    return _auto_update