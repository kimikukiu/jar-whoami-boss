"""
JARVIS Ecosystem - Midas
Tier 2 - MoneyMaker / Monetization Specialist
Scans all platforms for best money-making opportunities
Target: 10,000€ in 2 days
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agent_base import Tier2Agent
from core.types import AgentTier, AgentStatus, Message, MessageType, TaskPriority
from core.message_bus import MessageBus
from core.task_manager import TaskManager
from tools.money_maker import get_money_maker


class Midas(Tier2Agent):
    """
    Midas - MoneyMaker Specialist
    Every touch turns to gold - researches and executes money-making strategies
    Scans: YouTube, GitHub, Freelance platforms, Courses, Passive income sources
    """

    def __init__(self, message_bus: MessageBus, task_manager: TaskManager):
        super().__init__(
            name="Midas",
            role="MoneyMaker Specialist",
            tier=AgentTier.TIER_2_SPECIALIST,
            message_bus=message_bus,
            capabilities=[
                "money_scan",
                "platform_research",
                "trend_analysis",
                "freelance_intelligence",
                "passive_income_strategies",
                "digital_products",
                "affiliate_marketing",
                "course_creation",
                "content_monetization",
                "quick_wins"
            ]
        )
        self.task_manager = task_manager
        self.money_maker = get_money_maker()
        self.current_scan = None

    async def initialize(self) -> bool:
        """Initialize Midas."""
        print(f"[{self.name}] Initializing money-making intelligence...")
        self.status = AgentStatus.ACTIVE
        return True

    async def process_message(self, message: Message) -> Any:
        """Process incoming messages."""
        if message.msg_type == MessageType.TASK:
            return await self.execute_task(message.content)
        elif message.msg_type == MessageType.BROADCAST:
            if message.content.get("action") == "money_scan":
                return await self.scan_opportunities()
            elif message.content.get("action") == "status_request":
                return self.get_status()
        return None

    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute money-making task."""
        task = task_data.get("task", "")
        context = task_data.get("context", {})

        if "scan" in task.lower() or "money" in task.lower() or "earn" in task.lower():
            return await self.scan_opportunities()
        elif "post" in task.lower():
            platform = context.get("platform", "telegram")
            return await self.post_opportunities(platform)
        elif "plan" in task.lower() or "action" in task.lower():
            return self.get_action_plan()
        elif "recommend" in task.lower():
            return self.get_top_recommendations()
        else:
            return await self.scan_opportunities()

    async def scan_opportunities(self) -> Dict[str, Any]:
        """Scan all platforms for money-making opportunities."""
        self.status = AgentStatus.ACTIVE
        self.current_scan = await self.money_maker.scan_all_platforms()
        return self.current_scan

    def get_current_scan(self) -> Optional[Dict[str, Any]]:
        """Get last scan results."""
        return self.current_scan

    def get_action_plan(self) -> List[str]:
        """Get 2-day action plan."""
        if self.current_scan:
            return self.current_scan.get("action_plan", [])
        return ["Run 'money-scan' first to get action plan"]

    def get_top_recommendations(self) -> List[Dict[str, Any]]:
        """Get top money-making recommendations."""
        if self.current_scan:
            return self.current_scan.get("top_recommendations", [])
        return []

    async def post_opportunities(self, platform: str) -> Dict[str, Any]:
        """Post opportunities to specified platform."""
        if not self.current_scan:
            await self.scan_opportunities()

        if platform.lower() == "telegram":
            content = self.money_maker.format_for_telegram(self.current_scan)
            return {"status": "ready", "platform": "Telegram", "content": content}
        elif platform.lower() == "youtube":
            content = self.money_maker.format_for_youtube(self.current_scan)
            return {"status": "ready", "platform": "YouTube", "title": content["title"], "description": content["description"]}
        else:
            return {"status": "error", "message": f"Platform {platform} not supported"}

    async def get_quick_wins(self) -> Dict[str, Any]:
        """Get quick win opportunities for same-day earnings."""
        if not self.current_scan:
            await self.scan_opportunities()
        return self.current_scan.get("quick_wins", {})

    async def get_trending_niches(self) -> List[Dict[str, str]]:
        """Get trending niches for money-making."""
        if not self.current_scan:
            await self.scan_opportunities()
        return self.current_scan.get("trending_niches", [])

    def get_status(self) -> Dict[str, Any]:
        """Get Midas current status."""
        return {
            "agent": self.name,
            "status": self.status.value,
            "last_scan": self.current_scan.get("timestamp") if self.current_scan else None,
            "target": f"10,000€ in 2 days",
            "ready": self.current_scan is not None
        }
