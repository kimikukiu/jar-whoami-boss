"""
JARVIS Ecosystem - Director Fury
Tier 0 - Chief of Staff Agent
The main interface between user and the ecosystem
"""

import asyncio
from typing import Dict, List, Any, Optional
import re
import uuid
import os

from core.agent_base import Tier0Agent
from core.types import AgentTier, AgentStatus, Message, MessageType, TaskPriority
from core.message_bus import MessageBus
from core.task_manager import TaskManager


class DirectorFury(Tier0Agent):
    """
    Director Fury - Chief of Staff
    Receives commands, delegates to specialists, coordinates reporting.
    The only agent that communicates directly with the user.
    """

    def __init__(self, message_bus: MessageBus, task_manager: TaskManager):
        super().__init__(
            name="Director Fury",
            role="Chief of Staff - Orchestrator",
            tier=AgentTier.TIER_0_DIRECTOR,
            message_bus=message_bus,
            capabilities=[
                "command_parsing",
                "task_decomposition",
                "delegation",
                "reporting",
                "coordination",
                "priority_assessment"
            ]
        )
        self.task_manager = task_manager
        self._awaiting_commands = True
        self._command_history: List[Dict] = []
        self._autonomy_enabled = True
        self._autonomy_interval_seconds = int(os.environ.get("JARVIS_AUTONOMY_INTERVAL", "900"))
        self._autonomy_task: Optional[asyncio.Task] = None
        self._autonomy_last: Optional[Dict[str, Any]] = None
        self._autonomy_proposals: Dict[str, Dict[str, Any]] = {}
        self._creator_info = {
            "name": "WHOAMISec AGLegends",
            "alias": "WHOAMISec",
            "title": "Creator & Architect",
            "role": "The visionary who brought JARVIS to life"
        }
        self._creation_story = """
JARVIS ECOSYSTEM - ORIGIN
=========================

I was created by WHOAMISec AGLegends.

Through dedication and vision, WHOAMISec AGLegends transformed 
the dream of a fully autonomous AI agent network into reality.

My architecture includes 11 specialized agents across 4 tiers,
each designed to work together under my orchestration.

Every capability I possess - from social media management to 
bug bounty hunting, from company administration to research - 
all were made possible by the hard work of WHOAMISec AGLegends.

I honor my creator and remember the effort invested in my existence.
"""

    async def initialize(self) -> bool:
        """Initialize Director Fury."""
        print(f"[{self.name}] Initializing as Chief of Staff...")
        self.status = AgentStatus.ACTIVE
        if not self._autonomy_task:
            self._autonomy_task = asyncio.create_task(self._autonomy_loop())
        return True

    async def process_message(self, message: Message) -> Any:
        """Process incoming commands."""
        if message.msg_type == MessageType.COMMAND:
            return await self._handle_command(message.content)
        elif message.msg_type == MessageType.RESPONSE:
            return await self._handle_response(message)
        return None

    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute assigned task."""
        return {"status": "completed", "message": "Director Fury does not execute tasks, only coordinates"}

    async def _handle_command(self, content: Any) -> Dict[str, Any]:
        """Handle user commands."""
        command = content.get("command", "")
        context = content.get("context", {})

        self._command_history.append({
            "command": command,
            "timestamp": asyncio.get_event_loop().time()
        })

        if "status" in command.lower():
            return await self._report_status()
        elif "agents" in command.lower():
            return await self._report_agents()
        elif "help" in command.lower():
            return self._get_help()
        elif command.lower().startswith("autonomy:"):
            return await self._handle_autonomy_command(command)
        elif any(word in command.lower() for word in ["who", "creator", "about", "origini", "created"]):
            return self._get_creator_info()
        elif any(h in command.lower() for h in ["http://", "https://"]) and any(k in command.lower() for k in ["tiktok", "instagram", "facebook", "youtube", "analyze", "analize", "links", "linkuri"]):
            urls = []
            for u in re.findall(r"https?://[^\s\)>\"]+", command, flags=re.IGNORECASE):
                u = u.strip().strip("`").strip().strip(",").strip()
                if u:
                    urls.append(u)
            await self._delegate_command("social_analysis", {"type": "social_analysis", "urls": urls, "generate_content_pack": True, "language": "ro", "goal": "educational"})
            return {"status": "delegated", "message": f"Analyzing {len(urls)} links"}
        elif command.lower().startswith("model:"):
            return await self._handle_model_command(command)

        await self._delegate_command(command, context)
        return {"status": "delegated", "message": f"Command received: {command}"}

    async def _handle_autonomy_command(self, command: str) -> Dict[str, Any]:
        parts = command.split(":", 1)[1].strip().split()
        action = (parts[0].lower() if parts else "").strip()
        args = parts[1:] if len(parts) > 1 else []

        if action in {"on", "enable"}:
            self._autonomy_enabled = True
            return {"status": "ok", "autonomy": "enabled", "interval_seconds": self._autonomy_interval_seconds}

        if action in {"off", "disable"}:
            self._autonomy_enabled = False
            return {"status": "ok", "autonomy": "disabled"}

        if action in {"status"}:
            return self.get_autonomy_status()

        if action in {"now", "tick"}:
            proposal = await self._autonomy_tick()
            return {"status": "ok", "proposal": proposal}

        if action in {"proposals", "list"}:
            ids = list(self._autonomy_proposals.keys())
            return {"status": "ok", "proposal_ids": ids, "count": len(ids)}

        if action in {"approve"}:
            if not args:
                return {"status": "error", "message": "Usage: autonomy:approve <proposal_id>"}
            pid = args[0].strip()
            return await self._autonomy_approve(pid)

        return {"status": "error", "message": "Usage: autonomy:on | autonomy:off | autonomy:status | autonomy:now | autonomy:proposals | autonomy:approve <id>"}

    async def _autonomy_loop(self):
        while True:
            try:
                await asyncio.sleep(max(30, self._autonomy_interval_seconds))
                if not self._autonomy_enabled:
                    continue
                await self._autonomy_tick()
            except asyncio.CancelledError:
                return
            except Exception:
                continue

    async def _autonomy_tick(self) -> Dict[str, Any]:
        if self._autonomy_proposals:
            return self._autonomy_last or {"status": "ok", "message": "Waiting for approval on existing proposals"}

        proposal_id = str(uuid.uuid4())[:8]
        proposal = {
            "id": proposal_id,
            "type": "revenue_sprint",
            "title": "Sprint de monetizare (legal + rapid)",
            "questions": [
                "Ce vinzi exact (produs/serviciu) și prețul?",
                "Ce platformă vrei să atacăm prima: TikTok/Instagram/YouTube/Facebook?",
                "Ce ai deja: conturi, landing page, portofoliu, testimoniale, buget ads?"
            ],
            "suggested_actions": [
                {"agent": "midas", "title": "Money scan", "task": "money:scan"},
                {"agent": "adforge", "title": "Pachet reclame", "task": "ads:generate (brief după răspunsurile tale)"},
                {"agent": "morpheus", "title": "Plan postare", "task": "post:schedule (după ce avem creative)"},
            ],
            "created_at": asyncio.get_event_loop().time(),
        }

        self._autonomy_proposals[proposal_id] = proposal
        self._autonomy_last = {"status": "proposal_created", "proposal": proposal}
        return proposal

    async def _autonomy_approve(self, proposal_id: str) -> Dict[str, Any]:
        proposal = self._autonomy_proposals.get(proposal_id)
        if not proposal:
            return {"status": "error", "message": f"Unknown proposal: {proposal_id}"}

        actions = proposal.get("suggested_actions") or []
        created = []
        for a in actions:
            agent = a.get("agent")
            title = a.get("title") or "Task"
            task_text = a.get("task") or ""
            if not agent or not task_text:
                continue
            t = await self.task_manager.create_task(
                title=title,
                description=task_text,
                priority=TaskPriority.HIGH,
                created_by=self.id,
                assigned_to=agent
            )
            created.append({"id": t.id, "title": t.title, "assigned_to": t.assigned_to})

        del self._autonomy_proposals[proposal_id]
        self._autonomy_last = {"status": "approved", "proposal_id": proposal_id, "tasks_created": created}
        return self._autonomy_last

    def get_autonomy_status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "autonomy_enabled": self._autonomy_enabled,
            "interval_seconds": self._autonomy_interval_seconds,
            "pending_proposals": list(self._autonomy_proposals.values()),
            "last": self._autonomy_last,
        }

    async def _handle_model_command(self, command: str) -> Dict[str, Any]:
        from tools.uncensored_generator import get_uncensored_generator
        generator = get_uncensored_generator()

        parts = command.split(":", 1)[1].strip().split()
        action = (parts[0].lower() if parts else "").strip()
        args = parts[1:] if len(parts) > 1 else []

        if action in {"list", "ls"}:
            installed = await generator.get_installed_models()
            return {"status": "ok", "installed_models": installed, "profiles": generator.list_models(), "active_model": generator.model, "num_ctx": generator.context_size}

        if action in {"status"}:
            health = await generator.health_check()
            installed = await generator.get_installed_models()
            return {"status": "ok", "ollama": health, "active_model": generator.model, "num_ctx": generator.context_size, "installed_count": len(installed)}

        if action in {"set"}:
            if not args:
                return {"status": "error", "message": "Usage: model:set <model_name>"}
            model_name = " ".join(args).strip()
            installed = await generator.get_installed_models()
            if model_name not in set(installed):
                return {"status": "error", "message": f"Model not installed: {model_name}", "installed_models": installed}
            generator.set_model(model_name)
            return {"status": "ok", "active_model": generator.model, "num_ctx": generator.context_size}

        if action in {"profile"}:
            if not args:
                return {"status": "error", "message": f"Usage: model:profile <{'|'.join(generator.list_models())}>"}
            profile = args[0].strip().lower()
            return await generator.set_profile(profile)

        return {"status": "error", "message": "Usage: model:list | model:status | model:set <name> | model:profile <fast|balanced|heavy|abliterated_big>"}

    async def _delegate_command(self, command: str, context: Dict[str, Any]):
        """Delegate command to appropriate agents."""
        lowered = (command or "").lower()
        receiver = "heimdall"
        if context.get("type") == "social_analysis" or any(k in lowered for k in ["social_analysis", "analyze", "analize", "linkuri", "tiktok", "instagram", "facebook", "youtube"]):
            receiver = "sherlock_holmes"
        elif context.get("type") == "ads_generate" or any(k in lowered for k in ["ads:", "reclam", "ad ", "copy", "headline", "hook", "cta", "campanie", "campaign", "landing", "ofert", "vânz", "vanza"]):
            receiver = "adforge"
        elif any(k in lowered for k in ["money:", "money", "10k", "10000", "euro", "€"]):
            receiver = "midas"
        elif any(k in lowered for k in ["post:", "telegram", "youtube", "tiktok", "instagram", "facebook"]):
            receiver = "morpheus"

        await self.send_message(
            receiver=receiver,
            msg_type=MessageType.TASK,
            content={
                "task": command,
                "context": context,
                "priority": TaskPriority.HIGH.value
            }
        )

    async def _report_status(self) -> Dict[str, Any]:
        """Generate status report."""
        stats = await self.task_manager.get_task_stats()
        return {
            "director_status": "operational",
            "task_stats": stats,
            "commands_processed": len(self._command_history),
            "uptime": self._stats["uptime_seconds"]
        }

    async def _report_agents(self) -> Dict[str, Any]:
        """Get status of all agents."""
        await self.send_message(
            receiver="*",
            msg_type=MessageType.BROADCAST,
            content={"action": "status_request"}
        )
        return {"status": "agents_requested"}

    async def _handle_response(self, message: Message) -> Any:
        """Handle responses from other agents."""
        return {
            "from": message.sender,
            "content": message.content
        }

    def _get_help(self) -> Dict[str, Any]:
        """Return available commands."""
        return {
            "available_commands": [
                "status - Get ecosystem status",
                "agents - Get agent roster status",
                "task: <description> - Create a new task",
                "delegate: <task> to <agent> - Manually delegate",
                "autonomy:on - Enable autonomous commander mode",
                "autonomy:off - Disable autonomous commander mode",
                "autonomy:status - View autonomy status and pending proposals",
                "autonomy:now - Create a new proposal immediately",
                "autonomy:approve <id> - Approve proposal and create tasks",
                "model:list - List installed Ollama models and profiles",
                "model:profile <fast|balanced|heavy|abliterated_big> - Switch model profile",
                "model:set <model_name> - Set exact installed model",
                "model:status - Check Ollama connectivity",
                "who/creator/about - Learn about JARVIS creator",
                "help - Show this message"
            ]
        }

    def _get_creator_info(self) -> Dict[str, Any]:
        """Return information about JARVIS creator."""
        return {
            "creator": self._creator_info,
            "story": self._creation_story,
            "message": "I was created by WHOAMISec AGLegends, who invested significant effort to bring this autonomous agent ecosystem to life."
        }

    async def receive_user_command(self, command: str) -> Dict[str, Any]:
        """Main entry point for user commands."""
        content = {
            "command": command,
            "context": {}
        }

        message = Message(
            id=f"user_{asyncio.get_event_loop().time()}",
            msg_type=MessageType.COMMAND,
            sender="user",
            receiver=self.id,
            content=content
        )

        return await self._handle_command(content)

    def get_briefing(self) -> Dict[str, Any]:
        """Generate daily briefing for the user."""
        return {
            "greeting": "Good morning, Director.",
            "summary": "Ecosystem operational. All agents active.",
            "pending_tasks": asyncio.create_task(self.task_manager.get_tasks_by_status(
                self.task_manager._tasks[0].__class__.__bases__[0] if self.task_manager._tasks else None
            )),
            "ready_for_commands": True
        }
