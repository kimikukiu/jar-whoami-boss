"""
JARVIS Ecosystem - Agent Base Class
Base class for all agents in the ecosystem
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod

from .types import AgentStatus, AgentTier, Message, MessageType
from .message_bus import MessageBus


class AgentBase(ABC):
    """
    Base class for all JARVIS agents.
    Each agent has a specific role and responsibilities.
    """

    def __init__(
        self,
        name: str,
        role: str,
        tier: AgentTier,
        message_bus: MessageBus,
        capabilities: Optional[List[str]] = None
    ):
        self.id = name.lower().replace(" ", "_")
        self.name = name
        self.role = role
        self.tier = tier
        self.status = AgentStatus.STANDBY
        self.capabilities = capabilities or []
        self.message_bus = message_bus
        self._running = False
        self._current_task: Optional[str] = None
        self._stats: Dict[str, Any] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "uptime_seconds": 0
        }
        self._start_time = datetime.now()
        self._handlers: Dict[MessageType, Callable] = {}

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent. Override in subclasses."""
        pass

    @abstractmethod
    async def process_message(self, message: Message) -> Any:
        """Process an incoming message. Override in subclasses."""
        pass

    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute a task assigned to this agent. Override in subclasses."""
        pass

    async def start(self):
        """Start the agent."""
        if self._running:
            return

        self._running = True
        await self.message_bus.subscribe(self.id, self._handle_message)
        await self.initialize()
        print(f"[{self.name}] Agent started - Role: {self.role}")

    async def stop(self):
        """Stop the agent."""
        self._running = False
        self.status = AgentStatus.OFFLINE
        print(f"[{self.name}] Agent stopped")

    async def _handle_message(self, message: Message):
        """Handle incoming messages."""
        self._stats["messages_received"] += 1

        if message.msg_type == MessageType.TASK:
            self.status = AgentStatus.BUSY
            self._current_task = message.content.get("task_id")
            try:
                result = await self.execute_task(message.content)
                await self.send_response(message, {"status": "completed", "result": result})
                self._stats["tasks_completed"] += 1
            except Exception as e:
                await self.send_response(message, {"status": "failed", "error": str(e)})
                self._stats["tasks_failed"] += 1
            finally:
                self.status = AgentStatus.ACTIVE
                self._current_task = None

        elif message.msg_type == MessageType.COMMAND:
            result = await self.process_message(message)
            if message.sender != "system":
                await self.send_response(message, result)

        elif message.msg_type == MessageType.HEARTBEAT:
            pass

    async def send_message(
        self,
        receiver: str,
        msg_type: MessageType,
        content: Any,
        correlation_id: Optional[str] = None
    ):
        """Send a message to another agent."""
        await self.message_bus.send_message(
            msg_type=msg_type,
            sender=self.id,
            receiver=receiver,
            content=content,
            correlation_id=correlation_id
        )
        self._stats["messages_sent"] += 1

    async def send_response(self, original_message: Message, content: Any):
        """Send a response to a message."""
        await self.send_message(
            receiver=original_message.sender,
            msg_type=MessageType.RESPONSE,
            content=content,
            correlation_id=original_message.id
        )

    async def broadcast(self, msg_type: MessageType, content: Any):
        """Broadcast to all agents."""
        await self.send_message(
            receiver="*",
            msg_type=msg_type,
            content=content
        )

    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "tier": self.tier.value,
            "status": self.status.value,
            "current_task": self._current_task,
            "capabilities": self.capabilities,
            "stats": self._stats,
            "uptime_seconds": uptime
        }

    async def update_stats(self, key: str, value: Any):
        """Update agent statistics."""
        self._stats[key] = value

    @property
    def is_active(self) -> bool:
        return self.status == AgentStatus.ACTIVE

    @property
    def is_busy(self) -> bool:
        return self.status == AgentStatus.BUSY


class Tier0Agent(AgentBase):
    """Tier 0 - Director/Orchestrator agents."""
    pass


class Tier1Agent(AgentBase):
    """Tier 1 - Gatekeeper/Validation agents."""
    pass


class Tier2Agent(AgentBase):
    """Tier 2 - Specialist/Analysis agents."""
    pass


class Tier3Agent(AgentBase):
    """Tier 3 - Executor/Implementation agents."""
    pass