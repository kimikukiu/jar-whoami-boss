"""
JARVIS Ecosystem - John Kramer
Tier 2 - Planner Agent
Decomposes missions into step-by-step plans
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agent_base import Tier2Agent
from core.types import AgentTier, AgentStatus, Message, MessageType, TaskPriority
from core.message_bus import MessageBus
from core.task_manager import TaskManager


class JohnKramer(Tier2Agent):
    """
    John Kramer - Planner
    Decomposes complex missions into actionable step-by-step plans.
    The strategic mind of the JARVIS ecosystem.
    """

    def __init__(self, message_bus: MessageBus, task_manager: TaskManager):
        super().__init__(
            name="John Kramer",
            role="Planner - Mission Decomposition",
            tier=AgentTier.TIER_2_SPECIALIST,
            message_bus=message_bus,
            capabilities=[
                "task_decomposition",
                "strategic_planning",
                "dependency_analysis",
                "resource_estimation",
                "risk_assessment",
                "milestone_definition"
            ]
        )
        self.task_manager = task_manager
        self._plans: Dict[str, List[Dict]] = {}
        self._active_planning: Dict[str, Any] = {}

    async def initialize(self) -> bool:
        """Initialize John Kramer."""
        print(f"[{self.name}] Initializing planner protocols...")
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
        """Execute planning task."""
        task = task_data.get("task", "")
        context = task_data.get("context", {})
        validation = task_data.get("validation", {})

        plan = await self.create_plan(task, context)

        for step in plan["steps"]:
            await self.task_manager.create_task(
                title=step["title"],
                description=step["description"],
                priority=self._map_priority(step.get("priority", "medium")),
                created_by=self.id,
                parent_id=plan["id"]
            )

        self._plans[plan["id"]] = plan["steps"]

        return {
            "status": "planned",
            "plan_id": plan["id"],
            "steps": len(plan["steps"]),
            "estimated_time": plan.get("estimated_time", "unknown")
        }

    async def create_plan(self, mission: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed plan for a mission."""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        steps = self._decompose_mission(mission, context)

        plan = {
            "id": plan_id,
            "mission": mission,
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "estimated_time": self._estimate_time(steps),
            "risks": self._assess_risks(steps)
        }

        self._active_planning[plan_id] = plan

        return plan

    def _decompose_mission(self, mission: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose a mission into steps."""
        steps = []

        mission_lower = mission.lower()

        if any(word in mission_lower for word in ["build", "create", "make", "develop"]):
            steps.append({
                "title": "Sherlock - Analyze Requirements",
                "description": f"Analyze requirements for: {mission}",
                "priority": "high",
                "agent": "sherlock_holmes"
            })

        if any(word in mission_lower for word in ["fix", "bug", "error", "issue"]):
            steps.append({
                "title": "Ripley - Hunt Bugs",
                "description": f"Hunt bugs related to: {mission}",
                "priority": "critical",
                "agent": "ripley"
            })

        if any(word in mission_lower for word in ["design", "ui", "interface", "frontend"]):
            steps.append({
                "title": "Da Vinci - Design UI",
                "description": f"Design UI for: {mission}",
                "priority": "medium",
                "agent": "da_vinci"
            })

        steps.extend([
            {
                "title": "JARVIS - Validate Build",
                "description": "Validate code quality, type checking, lint",
                "priority": "high",
                "agent": "jarvis_build"
            },
            {
                "title": "Saul Goodman - Apply Patches",
                "description": "Apply necessary patches and fixes",
                "priority": "medium",
                "agent": "saul_goodman"
            },
            {
                "title": "John Wick - Final Implementation",
                "description": "Complete implementation and delivery",
                "priority": "high",
                "agent": "john_wick"
            }
        ])

        return steps

    def _estimate_time(self, steps: List[Dict]) -> str:
        """Estimate time for plan completion."""
        base_time_per_step = 15
        return f"{len(steps) * base_time_per_step} minutes"

    def _assess_risks(self, steps: List[Dict]) -> List[str]:
        """Assess risks in the plan."""
        risks = []
        if len(steps) > 5:
            risks.append("Complex plan - coordination overhead")
        if any(s.get("priority") == "critical" for s in steps):
            risks.append("Contains critical tasks - high impact if failure")
        return risks

    def _map_priority(self, priority: str) -> TaskPriority:
        """Map string priority to TaskPriority."""
        mapping = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "medium": TaskPriority.MEDIUM,
            "low": TaskPriority.LOW
        }
        return mapping.get(priority.lower(), TaskPriority.MEDIUM)

    def get_plan(self, plan_id: str) -> Optional[List[Dict]]:
        """Get a specific plan."""
        return self._plans.get(plan_id)

    def get_all_plans(self) -> Dict[str, List[Dict]]:
        """Get all plans."""
        return self._plans