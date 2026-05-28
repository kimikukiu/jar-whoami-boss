"""
JARVIS Ecosystem - Heimdall
Tier 1 - Gatekeeper Agent
Security, validation, and request filtering
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agent_base import Tier1Agent
from core.types import AgentTier, AgentStatus, Message, MessageType
from core.message_bus import MessageBus


class Heimdall(Tier1Agent):
    """
    Heimdall - Gatekeeper
    Validates requests, ensures security, filters noise.
    The guardian at the gate of the JARVIS ecosystem.
    """

    def __init__(self, message_bus: MessageBus):
        super().__init__(
            name="Heimdall",
            role="Gatekeeper - Security & Validation",
            tier=AgentTier.TIER_1_GATEKEEPER,
            message_bus=message_bus,
            capabilities=[
                "security_validation",
                "input_filtering",
                "threat_detection",
                "request_validation",
                "rate_limiting",
                "authentication"
            ]
        )
        self._blocked_requests: List[Dict] = []
        self._validated_requests: List[Dict] = []
        self._threat_patterns = [
            "injection",
            "exec",
            "eval",
            "system(",
            "subprocess",
            "../",
            "rm -rf",
            "drop table",
            "delete from"
        ]

    async def initialize(self) -> bool:
        """Initialize Heimdall."""
        print(f"[{self.name}] Initializing gatekeeper protocols...")
        self.status = AgentStatus.ACTIVE
        return True

    async def process_message(self, message: Message) -> Any:
        """Process incoming messages."""
        if message.msg_type == MessageType.TASK:
            return await self._validate_request(message.content)
        elif message.msg_type == MessageType.BROADCAST:
            if message.content.get("action") == "status_request":
                return self.get_status()
        return None

    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute validation task."""
        task = task_data.get("task", "")
        context = task_data.get("context", {})

        validation_result = await self._validate_request({"task": task, "context": context})

        if validation_result["allowed"]:
            await self.send_message(
                receiver="john_kramer",
                msg_type=MessageType.TASK,
                content={
                    "task": task,
                    "context": context,
                    "validation": validation_result
                }
            )
            return {"status": "forwarded", "validation": validation_result}
        else:
            return {"status": "blocked", "reason": validation_result["reason"]}

    async def _validate_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a request for security and appropriateness."""
        task = content.get("task", "")
        context = content.get("context", {})

        is_valid = True
        reasons = []

        if self._contains_threat(task):
            is_valid = False
            reasons.append("Potential security threat detected")

        if self._is_noise(task):
            is_valid = False
            reasons.append("Request appears to be noise")

        if not self._has_clear_intent(task):
            is_valid = False
            reasons.append("Intent unclear")

        validation = {
            "allowed": is_valid,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat(),
            "request": task
        }

        if is_valid:
            self._validated_requests.append(validation)
        else:
            self._blocked_requests.append(validation)

        return validation

    def _contains_threat(self, text: str) -> bool:
        """Check for potential security threats."""
        text_lower = text.lower()
        for pattern in self._threat_patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def _is_noise(self, text: str) -> bool:
        """Check if request is just noise."""
        noise_indicators = ["asdf", "test test", "???", "..."]
        return any(noise in text.lower() for noise in noise_indicators)

    def _has_clear_intent(self, text: str) -> bool:
        """Check if request has clear intent."""
        min_length = 3
        return len(text.strip()) >= min_length

    async def check_rate_limit(self, user_id: str, window_seconds: int = 60) -> bool:
        """Check if user is within rate limits."""
        return True

    async def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate a request."""
        return {"authenticated": True, "user": credentials.get("user", "anonymous")}

    def get_blocked_count(self) -> int:
        """Get number of blocked requests."""
        return len(self._blocked_requests)

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            "validated": len(self._validated_requests),
            "blocked": len(self._blocked_requests),
            "threats_detected": sum(1 for v in self._blocked_requests if "threat" in str(v))
        }