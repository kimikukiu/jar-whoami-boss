"""
JARVIS Ecosystem - Message Bus
Inter-agent communication system
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from .types import Message, MessageType


class MessageBus:
    """
    Central message bus for inter-agent communication.
    Supports publish/subscribe pattern with routing.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_history: List[Message] = []
        self._max_history: int = 1000
        self._lock = asyncio.Lock()
        self._routing_rules: Dict[str, str] = {}

    async def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe an agent to receive messages."""
        async with self._lock:
            self._subscribers[agent_id].append(callback)

    async def unsubscribe(self, agent_id: str, callback: Callable):
        """Unsubscribe an agent from messages."""
        async with self._lock:
            if agent_id in self._subscribers:
                self._subscribers[agent_id].remove(callback)

    async def publish(self, message: Message) -> bool:
        """Publish a message to the bus."""
        async with self._lock:
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history.pop(0)

        if message.receiver == "*":
            await self._broadcast(message)
        else:
            await self._route_message(message)

        return True

    async def _broadcast(self, message: Message):
        """Broadcast to all subscribers."""
        for agent_id, callbacks in self._subscribers.items():
            if message.sender != agent_id:
                for callback in callbacks:
                    try:
                        await callback(message)
                    except Exception as e:
                        print(f"Error delivering message to {agent_id}: {e}")

    async def _route_message(self, message: Message):
        """Route message to specific receiver."""
        if message.receiver in self._subscribers:
            for callback in self._subscribers[message.receiver]:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error delivering message to {message.receiver}: {e}")

    async def send_message(
        self,
        msg_type: MessageType,
        sender: str,
        receiver: str,
        content: Any,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Create and publish a message."""
        message = Message(
            id=str(uuid.uuid4()),
            msg_type=msg_type,
            sender=sender,
            receiver=receiver,
            content=content,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        await self.publish(message)
        return message

    async def get_messages(
        self,
        agent_id: Optional[str] = None,
        msg_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Message]:
        """Retrieve message history with filters."""
        async with self._lock:
            messages = self._message_history.copy()

        if agent_id:
            messages = [m for m in messages if m.sender == agent_id or m.receiver == agent_id or m.receiver == "*"]
        if msg_type:
            messages = [m for m in messages if m.msg_type == msg_type]

        return messages[-limit:]

    async def get_conversation(self, correlation_id: str) -> List[Message]:
        """Get all messages in a conversation thread."""
        async with self._lock:
            return [m for m in self._message_history if m.correlation_id == correlation_id]

    def add_routing_rule(self, pattern: str, destination: str):
        """Add a routing rule for message filtering."""
        self._routing_rules[pattern] = destination

    def clear_history(self):
        """Clear message history."""
        self._message_history.clear()

    async def broadcast_heartbeat(self, agent_id: str, status: Dict[str, Any]):
        """Send a heartbeat message."""
        await self.send_message(
            msg_type=MessageType.HEARTBEAT,
            sender=agent_id,
            receiver="*",
            content=status
        )

    async def broadcast_alert(self, agent_id: str, alert_type: str, message: str):
        """Send an alert to all agents."""
        await self.send_message(
            msg_type=MessageType.ALERT,
            sender=agent_id,
            receiver="*",
            content={"type": alert_type, "message": message}
        )