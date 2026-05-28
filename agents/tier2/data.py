"""
JARVIS Ecosystem - Data
Tier 2 - Archivist/Memory Agent
Persistent memory and context management
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from core.agent_base import Tier2Agent
from core.types import AgentTier, AgentStatus, Message, MessageType
from core.message_bus import MessageBus


class Data(Tier2Agent):
    """
    Data - Archivist
    Persistent memory, cross-referencing, and context management.
    The memory of the JARVIS ecosystem.
    """

    def __init__(self, message_bus: MessageBus, db_path: str = "jarvis_memory.json"):
        super().__init__(
            name="Data",
            role="Archivist - Memory & Context",
            tier=AgentTier.TIER_2_SPECIALIST,
            message_bus=message_bus,
            capabilities=[
                "memory_storage",
                "context_management",
                "cross_referencing",
                "entity_tracking",
                "history_management",
                "knowledge_graph"
            ]
        )
        self.db_path = db_path
        self._memory: Dict[str, Any] = {
            "entities": {},
            "interactions": [],
            "context_stack": [],
            "knowledge_graph": {}
        }
        self._load_memory()

    async def initialize(self) -> bool:
        """Initialize Data."""
        print(f"[{self.name}] Initializing memory systems...")
        self.status = AgentStatus.ACTIVE
        return True

    async def process_message(self, message: Message) -> Any:
        """Process incoming messages."""
        if message.msg_type == MessageType.TASK:
            return await self.execute_task(message.content)
        elif message.msg_type == MessageType.BROADCAST:
            if message.content.get("action") == "status_request":
                return self.get_status()
        return None

    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute memory task."""
        action = task_data.get("action", "")
        context = task_data.get("context", {})

        if action == "remember":
            return await self.remember(
                context.get("entity_type", "unknown"),
                context.get("entity_id", ""),
                context.get("data", {})
            )
        elif action == "recall":
            return await self.recall(
                context.get("entity_type", "unknown"),
                context.get("entity_id", "")
            )
        elif action == "forget":
            return await self.forget(
                context.get("entity_type", "unknown"),
                context.get("entity_id", "")
            )
        elif action == "cross_reference":
            return await self.cross_reference(
                context.get("entity_type", "unknown"),
                context.get("entity_id", "")
            )

        return {"status": "unknown_action"}

    async def remember(
        self,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store information in memory."""
        if entity_type not in self._memory["entities"]:
            self._memory["entities"][entity_type] = {}

        entity_key = f"{entity_type}_{entity_id}"
        self._memory["entities"][entity_type][entity_key] = {
            "data": data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0
        }

        self._memory["interactions"].append({
            "type": "remember",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat()
        })

        self._save_memory()

        return {
            "status": "remembered",
            "entity_type": entity_type,
            "entity_id": entity_id
        }

    async def recall(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Recall information from memory."""
        if entity_type not in self._memory["entities"]:
            return None

        entity_key = f"{entity_type}_{entity_id}"

        if entity_key in self._memory["entities"][entity_type]:
            entity = self._memory["entities"][entity_type][entity_key]
            entity["access_count"] += 1
            entity["updated_at"] = datetime.now().isoformat()
            self._save_memory()
            return entity

        return None

    async def forget(
        self,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, Any]:
        """Remove information from memory."""
        if entity_type in self._memory["entities"]:
            entity_key = f"{entity_type}_{entity_id}"
            if entity_key in self._memory["entities"][entity_type]:
                del self._memory["entities"][entity_type][entity_key]
                self._save_memory()
                return {"status": "forgotten"}

        return {"status": "not_found"}

    async def cross_reference(
        self,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, Any]:
        """Find related entities in memory."""
        primary = await self.recall(entity_type, entity_id)

        if not primary:
            return {"status": "not_found"}

        references = []
        data = primary.get("data", {})

        for other_type, entities in self._memory["entities"].items():
            for key, entity in entities.items():
                if key != f"{entity_type}_{entity_id}":
                    if self._entities_related(data, entity.get("data", {})):
                        references.append({
                            "type": other_type,
                            "id": key,
                            "data": entity.get("data", {})
                        })

        return {
            "entity": f"{entity_type}_{entity_id}",
            "primary": primary,
            "references": references
        }

    def _entities_related(self, data1: Dict, data2: Dict) -> bool:
        """Check if two entities are related."""
        common_keys = set(data1.keys()) & set(data2.keys())
        for key in common_keys:
            if data1[key] == data2[key]:
                return True
        return False

    async def push_context(self, context: Dict[str, Any]) -> str:
        """Push context to the context stack."""
        context_id = str(uuid.uuid4())[:8]
        self._memory["context_stack"].append({
            "id": context_id,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._save_memory()
        return context_id

    async def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop context from the context stack."""
        if self._memory["context_stack"]:
            context = self._memory["context_stack"].pop()
            self._save_memory()
            return context
        return None

    async def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context."""
        return {
            "context_stack_depth": len(self._memory["context_stack"]),
            "entities_count": sum(len(e) for e in self._memory["entities"].values()),
            "recent_interactions": self._memory["interactions"][-10:] if self._memory["interactions"] else []
        }

    def _save_memory(self):
        """Save memory to disk."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self._memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def _load_memory(self):
        """Load memory from disk."""
        try:
            with open(self.db_path, 'r') as f:
                self._memory = json.load(f)
        except FileNotFoundError:
            self._memory = {
                "entities": {},
                "interactions": [],
                "context_stack": [],
                "knowledge_graph": {}
            }
        except Exception as e:
            print(f"Error loading memory: {e}")
            self._memory = {
                "entities": {},
                "interactions": [],
                "context_stack": [],
                "knowledge_graph": {}
            }

    def get_all_entities(self, entity_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all entities, optionally filtered by type."""
        if entity_type:
            return self._memory["entities"].get(entity_type, {})
        return self._memory["entities"]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_entities": sum(len(e) for e in self._memory["entities"].values()),
            "by_type": {k: len(v) for k, v in self._memory["entities"].items()},
            "interactions_count": len(self._memory["interactions"]),
            "context_stack_depth": len(self._memory["context_stack"])
        }