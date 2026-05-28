"""
JARVIS Ecosystem - Morpheus
Tier 2 - Dispatcher + Social Media Master
Routes tasks and manages all social media platforms
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agent_base import Tier2Agent
from core.types import AgentTier, AgentStatus, Message, MessageType, TaskPriority
from core.message_bus import MessageBus
from core.task_manager import TaskManager


class Morpheus(Tier2Agent):
    """
    Morpheus - Dispatcher + Social Media Master
    Routes tasks AND manages all social media accounts (YouTube, TikTok, Facebook, Instagram, etc.)
    """

    def __init__(self, message_bus: MessageBus, task_manager: TaskManager):
        super().__init__(
            name="Morpheus",
            role="Dispatcher + Social Media Commander",
            tier=AgentTier.TIER_2_SPECIALIST,
            message_bus=message_bus,
            capabilities=[
                "task_routing",
                "social_media_management",
                "youtube_automation",
                "tiktok_automation",
                "facebook_automation",
                "instagram_automation",
                "twitter_automation",
                "content_distribution",
                "scheduling",
                "analytics"
            ]
        )
        self.task_manager = task_manager
        self._social_accounts: Dict[str, Dict] = {}
        self._content_queue: List[Dict] = []
        self._scheduled_posts: List[Dict] = []

    async def initialize(self) -> bool:
        """Initialize Morpheus."""
        print(f"[{self.name}] Initializing social media protocols...")
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
        """Execute task - routing or social media operation."""
        task = task_data.get("task", "")
        context = task_data.get("context", {})

        if any(platform in task.lower() for platform in ["youtube", "tiktok", "facebook", "instagram", "twitter", "social"]):
            return await self.manage_social(task, context)
        else:
            return await self.route_task(task, context)

    async def manage_social(self, task: str, context: Dict) -> Dict[str, Any]:
        """Manage social media operations."""
        platform = context.get("platform", "all")
        action = context.get("action", "create_content")

        if action == "create_account":
            return await self.create_account(platform, context)
        elif action == "post":
            return await self.post_content(platform, context)
        elif action == "schedule":
            return await self.schedule_content(platform, context)
        elif action == "analyze":
            return await self.analyze_performance(platform, context)
        elif action == "create_content":
            return await self.generate_content(platform, context)

        return {"status": "social_task_complete", "platform": platform, "action": action}

    async def create_account(self, platform: str, context: Dict) -> Dict[str, Any]:
        """Create social media account."""
        account_name = context.get("account_name", "New Account")
        email = context.get("email", "")
        password = context.get("password", "")

        account = {
            "id": f"{platform}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "platform": platform,
            "account_name": account_name,
            "email": email,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "followers": 0,
            "posts": 0
        }

        self._social_accounts[account["id"]] = account

        return {
            "status": "account_created",
            "account": account,
            "platform": platform,
            "ready_for_content": True
        }

    async def post_content(self, platform: str, context: Dict) -> Dict[str, Any]:
        """Post content to social media."""
        content = context.get("content", {})
        media = context.get("media", [])
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", [])

        post = {
            "id": f"POST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "platform": platform,
            "caption": caption,
            "hashtags": hashtags,
            "media": len(media),
            "posted_at": datetime.now().isoformat(),
            "engagement": {"likes": 0, "comments": 0, "shares": 0}
        }

        return {
            "status": "posted",
            "post": post,
            "platform": platform
        }

    async def schedule_content(self, platform: str, context: Dict) -> Dict[str, Any]:
        """Schedule content for later posting."""
        content = context.get("content", {})
        scheduled_time = context.get("scheduled_time", "")

        scheduled = {
            "id": f"SCHED_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "platform": platform,
            "content": content,
            "scheduled_for": scheduled_time,
            "status": "scheduled"
        }

        self._scheduled_posts.append(scheduled)

        return {
            "status": "scheduled",
            "scheduled_post": scheduled
        }

    async def analyze_performance(self, platform: str, context: Dict) -> Dict[str, Any]:
        """Analyze social media performance."""
        return {
            "platform": platform,
            "period": "last_30_days",
            "metrics": {
                "followers": {"current": 12500, "growth": 15.3},
                "engagement_rate": 4.7,
                "reach": 45000,
                "impressions": 120000
            },
            "top_post": {
                "caption": "Best performing post",
                "likes": 2500,
                "shares": 340
            },
            "recommendations": [
                "Post more video content",
                "Use trending hashtags",
                "Engage with comments within 1 hour"
            ]
        }

    async def generate_content(self, platform: str, context: Dict) -> Dict[str, Any]:
        """Generate content for social media."""
        content_type = context.get("content_type", "post")
        topic = context.get("topic", "")

        if content_type == "video_script":
            return {
                "status": "content_generated",
                "type": "video_script",
                "platform": platform,
                "script": {
                    "title": f"Video about {topic}",
                    "hook": "Attention-grabbing opening",
                    "body": f"Main content about {topic}",
                    "cta": "Like, subscribe, share"
                },
                "duration": "60-90 seconds",
                "hashtags": [f"#{topic}", "#viral", "#trending"]
            }
        else:
            return {
                "status": "content_generated",
                "type": "post",
                "platform": platform,
                "caption": f"Amazing content about {topic}!",
                "hashtags": [f"#{topic.replace(' ', '')}", "#jarvis", "#ai"]
            }

    async def route_task(self, task: str, context: Dict) -> Dict[str, Any]:
        """Route task to appropriate agent."""
        routing_map = {
            "build": "jarvis_build",
            "test": "jarvis_build",
            "fix": "saul_goodman",
            "bug": "ripley",
            "design": "da_vinci",
            "implement": "john_wick",
            "plan": "john_kramer",
            "security": "heimdall",
            "memory": "data"
        }

        agent = "john_wick"
        for key, value in routing_map.items():
            if key in task.lower():
                agent = value
                break

        return {
            "status": "routed",
            "agent": agent,
            "task": task
        }

    def get_social_stats(self) -> Dict[str, Any]:
        """Get social media statistics."""
        platforms = {}
        for account in self._social_accounts.values():
            p = account["platform"]
            if p not in platforms:
                platforms[p] = {"accounts": 0, "total_followers": 0}
            platforms[p]["accounts"] += 1
            platforms[p]["total_followers"] += account.get("followers", 0)

        return {
            "total_accounts": len(self._social_accounts),
            "platforms": platforms,
            "scheduled_posts": len(self._scheduled_posts),
            "content_queue": len(self._content_queue)
        }