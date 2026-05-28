"""
JARVIS Ecosystem - Da Vinci + Content Creator
Tier 3 - UI Agent + Full Content Generation
Design, video scripts, written content, marketing materials
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.agent_base import Tier3Agent
from core.types import AgentTier, AgentStatus, Message, MessageType
from core.message_bus import MessageBus


class DaVinci(Tier3Agent):
    """
    Da Vinci - UI Agent + Content Creation Master
    Designs, generates content, creates marketing materials, videos, scripts, designs.
    The creative genius of the JARVIS ecosystem.
    """

    def __init__(self, message_bus: MessageBus):
        super().__init__(
            name="Da Vinci",
            role="UI Agent + Content Creator",
            tier=AgentTier.TIER_3_EXECUTOR,
            message_bus=message_bus,
            capabilities=[
                "ui_design",
                "ux_design",
                "graphic_design",
                "video_production",
                "script_writing",
                "copywriting",
                "marketing_content",
                "brand_design",
                "motion_graphics",
                "3d_design"
            ]
        )
        self._designs: List[Dict] = []
        self._content_library: Dict[str, Any] = {}

    async def initialize(self) -> bool:
        """Initialize Da Vinci."""
        print(f"[{self.name}] Initializing creative protocols...")
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
        """Execute creative task."""
        task = task_data.get("task", "")
        context = task_data.get("context", {})
        content_type = context.get("content_type", "design")

        if content_type == "video":
            return await self.create_video_content(task, context)
        elif content_type == "script":
            return await self.write_script(task, context)
        elif content_type == "marketing":
            return await self.create_marketing_content(task, context)
        elif content_type == "design":
            return await self.create_design(task, context)
        elif content_type == "copy":
            return await self.write_copy(task, context)
        elif content_type == "uncensored":
            return await self.generate_uncensored_content(task, context)
        elif content_type == "adult":
            return await self.generate_adult_content(task, context)

        return await self.create_design(task, context)

    async def create_video_content(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Create video content - scripts, storyboards, thumbnails."""
        duration = context.get("duration", "60-90 seconds")
        style = context.get("style", "engaging")
        platform = context.get("platform", "youtube")

        video_content = {
            "title": f"Ultimate Guide to {topic}",
            "script": {
                "hook": f"Have you ever wondered about {topic}?",
                "intro": "Today we're diving deep into this fascinating topic...",
                "main_points": [
                    f"Point 1 about {topic}",
                    f"Point 2 about {topic}",
                    f"Point 3 about {topic}"
                ],
                "call_to_action": "Like, subscribe, and hit that bell!"
            },
            "storyboard": [
                {"scene": 1, "description": "Eye-catching thumbnail with text overlay", "duration": "3s"},
                {"scene": 2, "description": "Host introduction", "duration": "5s"},
                {"scene": 3, "description": f"Content about {topic}", "duration": "60s"},
                {"scene": 4, "description": "Call to action", "duration": "5s"}
            ],
            "thumbnail": {
                "description": f"Image with bold text: '{topic}' and expressive face",
                "colors": ["#FF6B6B", "#4ECDC4", "#FFE66D"]
            },
            "seo_tags": [topic, "guide", "tutorial", "2024", "viral"],
            "estimated_views": 50000,
            "platform": platform
        }

        self._content_library[f"video_{topic}"] = video_content

        return {
            "status": "video_content_created",
            "content": video_content,
            "ready_for_production": True
        }

    async def write_script(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Write any type of script - video, podcast, presentation, etc."""
        script_type = context.get("script_type", "video")
        tone = context.get("tone", "professional")
        length = context.get("length", "medium")

        script = {
            "type": script_type,
            "topic": topic,
            "tone": tone,
            "sections": {
                "opening": f"[{topic}] - Opening hook that grabs attention",
                "introduction": "Welcome, everyone! Today we're discussing an important topic.",
                "main_content": self._generate_main_content(topic, length),
                "conclusion": "In conclusion, remember these key takeaways.",
                "call_to_action": "Don't forget to like, share, and subscribe!"
            },
            "estimated_duration": "5-10 minutes" if length == "medium" else "10-20 minutes",
            "word_count": 1500 if length == "medium" else 3000
        }

        return {
            "status": "script_written",
            "script": script,
            "ready_for_recording": True
        }

    def _generate_main_content(self, topic: str, length: str) -> str:
        """Generate main content sections."""
        if length == "short":
            return f"Key insight about {topic}: It's revolutionary and changing everything."
        elif length == "medium":
            return f"Three main points about {topic}: First, it's innovative. Second, it's practical. Third, it's the future."
        else:
            return f"Comprehensive analysis of {topic} covering history, current state, and future implications with detailed examples and case studies."

    async def create_marketing_content(self, product: str, context: Dict) -> Dict[str, Any]:
        """Create complete marketing campaign content."""
        platform = context.get("platform", "all")
        audience = context.get("audience", "general")

        marketing = {
            "headline": f"Transform Your Business with {product}",
            "tagline": "The solution you've been waiting for",
            "body_copy": {
                "problem": f"Struggling with challenges that {product} solves?",
                "solution": f"{product} provides the answer you've been looking for.",
                "benefits": [
                    "Increase efficiency by 200%",
                    "Save time and money",
                    "Easy to implement"
                ],
                "social_proof": "Join 10,000+ satisfied customers"
            },
            "cta_buttons": ["Get Started", "Learn More", "Contact Sales"],
            "email_sequence": {
                "subject_lines": [
                    f"Discover {product}",
                    "Last chance for exclusive offer",
                    "Your free trial awaits"
                ],
                "sequences": 5
            },
            "social_posts": [
                {"platform": "Twitter", "content": f"Exciting news about {product}! [link]"},
                {"platform": "Instagram", "content": f"Transform your workflow with {product} #business #innovation"},
                {"platform": "LinkedIn", "content": f"Why {product} is changing the game [article]"}
            ],
            "landing_page_elements": {
                "hero": f"Master Headline for {product}",
                "features": ["Feature 1", "Feature 2", "Feature 3"],
                "testimonials": ["Testimonial 1", "Testimonial 2"],
                "pricing": "Starting at $99/month"
            }
        }

        return {
            "status": "marketing_campaign_created",
            "campaign": marketing,
            "platforms": ["email", "social", "landing_page"]
        }

    async def create_design(self, subject: str, context: Dict) -> Dict[str, Any]:
        """Create design - UI, logo, brand elements."""
        design_type = context.get("design_type", "ui")

        design = {
            "type": design_type,
            "subject": subject,
            "color_palette": {
                "primary": "#4A9EFF",
                "secondary": "#9B59FF",
                "accent": "#00D4FF",
                "background": "#0A0A0F",
                "text": "#FFFFFF"
            },
            "typography": {
                "headings": "Orbitron",
                "body": "Rajdhani",
                "code": "Fira Code"
            },
            "elements": {
                "buttons": "Rounded with glow effect",
                "cards": "Glassmorphism with border glow",
                "gradients": "Neon blue to purple"
            },
            "specifications": {
                "resolution": "4K ready",
                "format": "SVG + PNG export",
                "theme": "RPG 3D Obsidian"
            }
        }

        self._designs.append(design)

        return {
            "status": "design_created",
            "design": design,
            "files_generated": ["source.svg", "preview.png", "specs.json"]
        }

    async def write_copy(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Write copy - ads, descriptions, product pages."""
        copy_type = context.get("copy_type", "ad")

        copy = {
            "type": copy_type,
            "headline": f"Revolutionary {topic}",
            "subheadline": "The future is here",
            "body": f"Discover how {topic} can transform your life. Join thousands who have already made the switch.",
            "cta": "Get Started Now",
            "testimonials": [
                {"author": "John D.", "quote": f"Best decision I ever made regarding {topic}"},
                {"author": "Sarah M.", "quote": f"Incredible results with {topic}"}
            ]
        }

        return {
            "status": "copy_written",
            "copy": copy
        }

    async def generate_uncensored_content(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Generate UNCENSORED content using Ollama abliterated models"""
        try:
            from tools.uncensored_generator import get_uncensored_generator
            generator = get_uncensored_generator()

            content_type = context.get("type", "story")
            explicit = context.get("explicit", True)

            if content_type == "story":
                content = await generator.generate_adult_story(
                    premise=topic,
                    style=context.get("style", "literary"),
                    length=context.get("length", "medium")
                )
            elif content_type == "script":
                result = await generator.generate_script(
                    topic=topic,
                    genre=context.get("genre", "drama"),
                    duration_minutes=context.get("duration", 90),
                    explicit=explicit
                )
                content = result.get("script", "")
            else:
                content = await generator.generate(topic)

            return {
                "status": "uncensored_content_generated",
                "topic": topic,
                "content_type": content_type,
                "explicit": explicit,
                "model_used": generator.model,
                "content": content[:5000] if len(content) > 5000 else content,
                "full_length": len(content)
            }
        except Exception as e:
            return {
                "status": "generation_failed",
                "error": str(e),
                "hint": "Ensure Ollama is running with uncensored models"
            }

    async def generate_adult_content(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Generate adult content - FULLY UNCENSORED via Ollama"""
        try:
            from tools.uncensored_generator import get_uncensored_generator
            generator = get_uncensored_generator()
            generator.set_model("hermes3:8b")

            premise = context.get("premise", topic)
            style = context.get("style", "literary")
            length = context.get("length", "medium")

            content = await generator.generate_adult_story(
                premise=premise,
                style=style,
                length=length
            )

            return {
                "status": "adult_content_generated",
                "premise": premise,
                "style": style,
                "length": length,
                "model_used": generator.model,
                "content": content[:5000] if len(content) > 5000 else content,
                "full_length": len(content),
                "uncensored": True
            }
        except Exception as e:
            return {
                "status": "generation_failed",
                "error": str(e),
                "hint": "Ensure Ollama is running with SARAH or other abliterated models"
            }

    def get_content_library(self) -> Dict[str, Any]:
        """Get all created content."""
        return {
            "total_pieces": len(self._content_library),
            "designs": len(self._designs),
            "library": self._content_library
        }