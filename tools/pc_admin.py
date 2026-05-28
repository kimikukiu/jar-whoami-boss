"""
JARVIS Ecosystem - PC Admin Control System
Full system control capabilities for Windows administration
"""

import os
import sys
import subprocess
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import winreg
    import ctypes
    import psutil
    WINDOWS = True
except ImportError:
    WINDOWS = False


class PCAdminControl:
    """
    JARVIS PC Admin Control System
    Provides full administrative control over the PC
    """

    def __init__(self):
        self._is_admin = False
        self._system_info = {}
        self._admin_commands = {
            "processes": self._get_processes,
            "services": self._get_services,
            "network": self._get_network,
            "firewall": self._get_firewall_status,
            "users": self._get_users,
            "installed": self._get_installed_software,
            "disk": self._get_disk_usage,
            "memory": self._get_memory_info,
            "cpu": self._get_cpu_info
        }

    def check_admin(self) -> bool:
        """Check if running with admin privileges."""
        if WINDOWS:
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                self._is_admin = bool(is_admin)
                return self._is_admin
            except:
                return False
        return os.getuid() == 0 if hasattr(os, 'getuid') else False

    def run_admin_command(self, command: str) -> Dict[str, Any]:
        """Execute administrative command."""
        if not self._is_admin:
            return {"error": "Admin privileges required", "status": "denied"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "status": "success",
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def control_process(self, action: str, pid: Optional[int] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Control processes - start, stop, restart."""
        if action == "list":
            return await self._get_processes()
        elif action == "kill" and pid:
            return await self._kill_process(pid)
        elif action == "start" and name:
            return await self._start_process(name)
        elif action == "restart" and pid:
            return await self._restart_process(pid)
        return {"status": "unknown_action"}

    async def _get_processes(self) -> Dict[str, Any]:
        """Get running processes."""
        if WINDOWS:
            try:
                import psutil
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except:
                        pass
                return {"status": "success", "processes": processes, "count": len(processes)}
            except:
                pass

        result = self.run_admin_command("tasklist /FO CSV /NH")
        return {"status": "success", "raw": result}

    async def _kill_process(self, pid: int) -> Dict[str, Any]:
        """Kill a process by PID."""
        if WINDOWS:
            result = self.run_admin_command(f"taskkill /F /PID {pid}")
            return result
        return {"status": "error", "message": "Windows only"}

    async def _start_process(self, name: str) -> Dict[str, Any]:
        """Start a process."""
        if WINDOWS:
            result = self.run_admin_command(f'start "" "{name}"')
            return result
        return {"status": "error", "message": "Windows only"}

    async def _restart_process(self, pid: int) -> Dict[str, Any]:
        """Restart a process."""
        await self._kill_process(pid)
        await asyncio.sleep(1)
        return {"status": "restarted", "pid": pid}

    async def _get_services(self) -> Dict[str, Any]:
        """Get Windows services."""
        if WINDOWS:
            result = self.run_admin_command("sc query state= all")
            return {"status": "success", "services": result}
        return {"status": "unsupported"}

    async def _get_network(self) -> Dict[str, Any]:
        """Get network connections and status."""
        if WINDOWS:
            result = self.run_admin_command("netstat -ano")
            return {"status": "success", "connections": result}
        return {"status": "unsupported"}

    async def _get_firewall_status(self) -> Dict[str, Any]:
        """Get Windows Firewall status."""
        if WINDOWS:
            result = self.run_admin_command("netsh advfirewall show allprofiles")
            return {"status": "success", "firewall": result}
        return {"status": "unsupported"}

    async def _get_users(self) -> Dict[str, Any]:
        """Get system users."""
        if WINDOWS:
            result = self.run_admin_command("net user")
            return {"status": "success", "users": result}
        return {"status": "unsupported"}

    async def _get_installed_software(self) -> Dict[str, Any]:
        """Get installed software list."""
        if WINDOWS:
            software = []
            try:
                reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path):
                    pass
            except:
                pass

            result = self.run_admin_command('powershell "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall* | Select-Object DisplayName, DisplayVersion, Publisher"')
            return {"status": "success", "software": result}

        return {"status": "unsupported"}

    async def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information."""
        if WINDOWS:
            result = self.run_admin_command("wmic logicaldisk get size,freespace,caption")
            return {"status": "success", "disk": result}
        return {"status": "unsupported"}

    async def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "status": "success",
                "memory": {
                    "total": mem.total,
                    "available": mem.available,
                    "percent": mem.percent,
                    "used": mem.used
                }
            }
        except:
            return {"status": "error"}

    async def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        try:
            import psutil
            return {
                "status": "success",
                "cpu": {
                    "count": psutil.cpu_count(),
                    "percent": psutil.cpu_percent(interval=1),
                    "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
                }
            }
        except:
            return {"status": "error"}

    async def system_control(self, action: str) -> Dict[str, Any]:
        """Execute system control actions."""
        if not self._is_admin:
            return {"error": "Admin privileges required"}

        if action == "shutdown":
            if WINDOWS:
                result = self.run_admin_command("shutdown /s /t 0")
                return {"status": "shutdown_initiated", "result": result}
        elif action == "restart":
            if WINDOWS:
                result = self.run_admin_command("shutdown /r /t 0")
                return {"status": "restart_initiated", "result": result}
        elif action == "sleep":
            if WINDOWS:
                result = self.run_admin_command("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return {"status": "sleep_initiated", "result": result}
        elif action == "lock":
            if WINDOWS:
                result = self.run_admin_command("rundll32.exe user32.dll,LockWorkStation")
                return {"status": "locked", "result": result}

        return {"status": "unknown_action"}

    async def registry_edit(self, action: str, path: str, key: str, value: str) -> Dict[str, Any]:
        """Edit Windows Registry."""
        if not self._is_admin or not WINDOWS:
            return {"error": "Admin privileges and Windows required"}

        if action == "set":
            cmd = f'reg add "{path}" /v {key} /t REG_SZ /d "{value}" /f'
            result = self.run_admin_command(cmd)
            return result
        elif action == "get":
            cmd = f'reg query "{path}" /v {key}'
            result = self.run_admin_command(cmd)
            return result
        elif action == "delete":
            cmd = f'reg delete "{path}" /v {key} /f'
            result = self.run_admin_command(cmd)
            return result

        return {"status": "unknown_action"}

    async def file_operations(self, action: str, path: str, new_path: Optional[str] = None) -> Dict[str, Any]:
        """File operations with admin privileges."""
        if not self._is_admin:
            return {"error": "Admin privileges required"}

        if action == "delete":
            cmd = f'del /f /q "{path}"'
            result = self.run_admin_command(cmd)
            return result
        elif action == "rename":
            cmd = f'ren "{path}" "{new_path}"'
            result = self.run_admin_command(cmd)
            return result
        elif action == "copy":
            cmd = f'copy /y "{path}" "{new_path}"'
            result = self.run_admin_command(cmd)
            return result
        elif action == "move":
            cmd = f'move /y "{path}" "{new_path}"'
            result = self.run_admin_command(cmd)
            return result

        return {"status": "unknown_action"}

    def get_system_info(self) -> Dict[str, Any]:
        """Get full system information."""
        return {
            "is_admin": self._is_admin,
            "platform": "Windows" if WINDOWS else "Linux",
            "hostname": os.environ.get("COMPUTERNAME", os.uname().nodename) if not WINDOWS else os.environ.get("COMPUTERNAME"),
            "user": os.environ.get("USERNAME", os.getlogin()),
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_admin_control = None

def get_admin_control() -> PCAdminControl:
    """Get admin control singleton."""
    global _admin_control
    if _admin_control is None:
        _admin_control = PCAdminControl()
    return _admin_control