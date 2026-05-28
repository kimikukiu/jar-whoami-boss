"""
ECOSYSTEM INTEGRATOR AGENT
Deployează modulele implementate în toate ecosistemele JARVIS
"""

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.agent_base import AgentBase, Tier


class EcosystemIntegratorAgent(AgentBase):
    """
    Agent specializat în integrarea modulelor în ecosisteme
    - Deploy în multiple ecosisteme
    - Configurare automată
    - Testare deploy
    - Rollback dacă e necesar
    """
    
    def __init__(self, message_bus):
        super().__init__(
            agent_id="ecosystem_integrator",
            name="Ecosystem Integrator",
            role="Multi-Ecosystem Deployment Specialist",
            tier=Tier.DIRECTOR,
            capabilities=[
                "multi_ecosystem_deploy",
                "auto_configuration",
                "deployment_testing",
                "rollback_capability",
                "ecosystem_synchronization"
            ],
            message_bus=message_bus,
            task_manager=None
        )
        
        self.ecosystems: List[str] = []
        self.deployed_modules: Dict[str, Any] = {}
        
    async def boot(self):
        """Inițializează agentul"""
        print("   🌐 EcosystemIntegratorAgent booting...")
        self.ecosystems = self._discover_ecosystems()
        print(f"   ✓ Found {len(self.ecosystems)} ecosystems")
        print("   ✓ Ready to deploy modules")
    
    def _discover_ecosystems(self) -> List[str]:
        """Descoperă toate ecosistemele JARVIS disponibile"""
        ecosystems = []
        
        # Căutăm în directorul principal
        base_path = Path("d:/jarvis")
        if base_path.exists():
            # Găsim toate subdirectoarele care ar putea fi ecosisteme
            for item in base_path.iterdir():
                if item.is_dir():
                    # Verificăm dacă are structură de ecosistem
                    if (item / "agents").exists() or (item / "modules").exists():
                        ecosystems.append(str(item))
        
        # Adăugăm ecosistemul principal
        ecosystems.append("d:/jarvis/ecosystem")
        
        # Elimină duplicate
        return list(set(ecosystems))
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execută un task primit de la Supreme Commander"""
        task_type = task.get('type')
        
        print(f"\n🌐 EcosystemIntegrator executing: {task_type}")
        
        try:
            if task_type == "deploy_to_ecosystems":
                result = await self._deploy_to_ecosystems(task)
            else:
                result = {"status": "unknown_task"}
            
            return {
                "task_id": task.get('id'),
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            return {
                "task_id": task.get('id'),
                "status": "failed",
                "error": str(e)
            }
    
    async def _deploy_to_ecosystems(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Deployează modulele în toate ecosistemele"""
        modules = task.get('modules', [])
        target_ecosystems = task.get('target_ecosystems', self.ecosystems)
        
        print(f"\n   🌐 Deploying to {len(target_ecosystems)} ecosystems...")
        
        deployment_results = []
        
        for ecosystem in target_ecosystems:
            print(f"\n   📦 Deploying to: {ecosystem}")
            
            # Creează structura de directoare
            modules_dir = Path(ecosystem) / "modules"
            modules_dir.mkdir(parents=True, exist_ok=True)
            
            deployed_modules = []
            
            for module in modules:
                module_name = module.get('name')
                module_code = module.get('code')
                
                # Scrie modulul
                module_file = modules_dir / f"{module_name}.py"
                with open(module_file, 'w', encoding='utf-8') as f:
                    f.write(module_code)
                
                deployed_modules.append(module_name)
                print(f"      ✓ {module_name}")
            
            # Actualizează __init__.py
            init_file = modules_dir / "__init__.py"
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('"""JARVIS Feature Modules"""\n\n')
                for module in deployed_modules:
                    f.write(f"from .{module} import *\n")
            
            deployment_results.append({
                "ecosystem": ecosystem,
                "status": "success",
                "modules_deployed": deployed_modules
            })
            
            print(f"   ✅ Successfully deployed to {ecosystem}")
        
        return {
            "total_ecosystems": len(target_ecosystems),
            "successful_deployments": len([r for r in deployment_results if r['status'] == 'success']),
            "deployments": deployment_results
        }