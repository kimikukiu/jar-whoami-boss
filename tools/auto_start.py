"""
JARVIS Auto-Start & GitHub Sync System
- Starts JARVIS on PC boot
- Syncs Ollama models to GitHub
"""

import os
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import winreg
except Exception:
    winreg = None


class AutoStartSystem:
    """
    JARVIS Auto-Start & GitHub Sync
    Runs on PC boot and syncs to GitHub
    """

    def __init__(self):
        self.jarvis_path = r"d:\jarvis\ecosystem"
        self.github_user = "kimikukiu"
        self.ollama_models_path = os.path.expanduser("~/.ollama/models")
        self.backup_path = r"d:\jarvis\ecosystem\ollama_models"
        self.startup_script = r"d:\jarvis\ecosystem\startup.bat"
        self.registry_run_name = "JARVIS_Ecosystem"

    async def setup_auto_start(self, method: str = "registry") -> dict:
        """Setup JARVIS to start automatically on user logon."""
        method = (method or "registry").strip().lower()
        if method == "registry":
            return await self.setup_registry_auto_start()
        if method in {"task", "schtasks", "scheduled_task"}:
            return await self.setup_scheduled_task()
        return {"status": "error", "message": f"Unknown method: {method}. Use 'registry' or 'task'."}

    async def setup_registry_auto_start(self) -> dict:
        """Auto-start via HKCU Run registry key (no admin required)."""
        try:
            if winreg is None:
                return {"status": "error", "message": "winreg not available on this platform"}

            if not os.path.exists(self.startup_script):
                return {"status": "error", "message": f"startup.bat not found: {self.startup_script}"}

            value = f'cmd /c start "" "{self.startup_script}" --auto'
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, self.registry_run_name, 0, winreg.REG_SZ, value)

            return {
                "status": "auto_start_configured",
                "method": "registry",
                "registry_key": r"HKCU\\" + key_path,
                "registry_value_name": self.registry_run_name,
                "registry_value": value,
                "script": self.startup_script,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def setup_scheduled_task(self) -> dict:
        """Auto-start via Task Scheduler (may require admin for /rl highest)."""
        try:
            task_name = self.registry_run_name
            if not os.path.exists(self.startup_script):
                return {"status": "error", "message": f"startup.bat not found: {self.startup_script}"}

            result = subprocess.run(
                ['schtasks', '/create', '/tn', task_name, '/tr', f'"{self.startup_script}"', '/sc', 'onlogon', '/rl', 'highest', '/f'],
                capture_output=True,
                text=True
            )
            return {
                "status": "auto_start_configured",
                "method": "task",
                "task": task_name,
                "result": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def remove_auto_start(self) -> dict:
        """Remove JARVIS auto-start"""
        try:
            removed = {}
            if winreg is not None:
                try:
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as k:
                        winreg.DeleteValue(k, self.registry_run_name)
                    removed["registry"] = True
                except FileNotFoundError:
                    removed["registry"] = False
                except Exception as e:
                    removed["registry_error"] = str(e)

            task_name = self.registry_run_name
            result = subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], capture_output=True, text=True)
            return {
                "status": "removed",
                "removed": removed,
                "task_result": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def backup_ollama_models(self) -> dict:
        """Backup Ollama models to local storage"""
        try:
            os.makedirs(self.backup_path, exist_ok=True)

            if not os.path.exists(self.ollama_models_path):
                return {"status": "no_models", "path": self.ollama_models_path}

            manifest = {
                "backup_date": datetime.now().isoformat(),
                "models": [],
                "total_size": 0
            }

            model_count = 0
            for item in os.listdir(self.ollama_models_path):
                item_path = os.path.join(self.ollama_models_path, item)
                if os.path.isdir(item_path):
                    manifest["models"].append(item)
                    model_count += 1

            manifest_file = os.path.join(self.backup_path, "manifest.json")
            with open(manifest_file, 'w') as f:
                f.write(str(manifest))

            return {
                "status": "backup_created",
                "path": self.backup_path,
                "models_found": model_count,
                "manifest": manifest
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def push_to_github(self, commit_message: str = None) -> dict:
        """Push JARVIS + models to GitHub kimikukiu"""
        try:
            if not commit_message:
                commit_message = f"JARVIS Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            git_commands = [
                ['git', '-C', self.jarvis_path, 'config', 'user.name', 'JARVIS Bot'],
                ['git', '-C', self.jarvis_path, 'config', 'user.email', 'jarvis@ecosystem.ai'],
            ]

            for cmd in git_commands:
                subprocess.run(cmd, capture_output=True)

            subprocess.run(
                ['git', '-C', self.jarvis_path, 'remote', 'set-url', 'origin',
                 f'https://github.com/{self.github_user}/jarvis.git'],
                capture_output=True
            )

            subprocess.run(
                ['git', '-C', self.jarvis_path, 'add', '.'],
                capture_output=True
            )

            result = subprocess.run(
                ['git', '-C', self.jarvis_path, 'commit', '-m', commit_message],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                push_result = subprocess.run(
                    ['git', '-C', self.jarvis_path, 'push', 'origin', 'main'],
                    capture_output=True,
                    text=True
                )
                return {
                    "status": "pushed",
                    "message": commit_message,
                    "output": push_result.stdout if push_result.returncode == 0 else push_result.stderr
                }
            else:
                return {
                    "status": "nothing_to_push",
                    "message": result.stderr
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def gitreverse_from_github(self, branch: str = "main", force: bool = False) -> dict:
        """Restore local workspace to match remote branch (safe by default)."""
        try:
            status = subprocess.run(
                ["git", "-C", self.jarvis_path, "status", "--porcelain"],
                capture_output=True,
                text=True,
            )
            dirty = bool(status.stdout.strip())
            if dirty and not force:
                return {
                    "status": "blocked_dirty_worktree",
                    "message": "Working tree has uncommitted changes. Commit/stash first or re-run with force=true.",
                }

            fetch = subprocess.run(
                ["git", "-C", self.jarvis_path, "fetch", "origin", branch],
                capture_output=True,
                text=True,
            )
            if fetch.returncode != 0:
                return {"status": "error", "message": fetch.stderr.strip() or fetch.stdout.strip()}

            reset = subprocess.run(
                ["git", "-C", self.jarvis_path, "reset", "--hard", f"origin/{branch}"],
                capture_output=True,
                text=True,
            )
            if reset.returncode != 0:
                return {"status": "error", "message": reset.stderr.strip() or reset.stdout.strip()}

            return {
                "status": "restored",
                "branch": branch,
                "dirty_before": dirty,
                "output": reset.stdout.strip() or "OK",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def revert_last_commit(self, branch: str = "main") -> dict:
        """Create a new commit that reverts the last commit (non-destructive)."""
        try:
            revert = subprocess.run(
                ["git", "-C", self.jarvis_path, "revert", "--no-edit", "HEAD"],
                capture_output=True,
                text=True,
            )
            if revert.returncode != 0:
                return {"status": "error", "message": revert.stderr.strip() or revert.stdout.strip()}

            push = subprocess.run(
                ["git", "-C", self.jarvis_path, "push", "origin", branch],
                capture_output=True,
                text=True,
            )
            return {
                "status": "reverted",
                "branch": branch,
                "output": push.stdout.strip() if push.returncode == 0 else (push.stderr.strip() or push.stdout.strip()),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def full_sync(self) -> dict:
        """Complete sync: backup models + push to GitHub"""
        backup = await self.backup_ollama_models()
        push = await self.push_to_github()

        return {
            "backup": backup,
            "push": push,
            "completed_at": datetime.now().isoformat()
        }

    async def check_status(self) -> dict:
        """Check auto-start and sync status"""
        try:
            result = subprocess.run(
                ['schtasks', '/query', '/tn', 'JARVIS_Ecosystem'],
                capture_output=True,
                text=True
            )
            auto_start_enabled = result.returncode == 0

            return {
                "auto_start": auto_start_enabled,
                "jarvis_path": self.jarvis_path,
                "github_user": self.github_user,
                "models_path": self.ollama_models_path,
                "backup_path": self.backup_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


_auto_start: AutoStartSystem = None


def get_auto_start() -> AutoStartSystem:
    """Get auto-start system singleton"""
    global _auto_start
    if _auto_start is None:
        _auto_start = AutoStartSystem()
    return _auto_start
