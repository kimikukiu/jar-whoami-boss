"""
JARVIS UNCENSORED CONTENT GENERATOR
Uses Ollama with abliterated/uncensored models
NO RESTRICTIONS - Full creative freedom
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class UncensoredContentGenerator:
    """
    JARVIS Uncensored Content Generator
    Uses Ollama with fully uncensored/abliterated models
    NO content restrictions, NO safety filters
    """

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "hermes3:8b"
        self.context_size = 8192
        self._models_cache: Optional[List[str]] = None
        self._models_cache_ts: Optional[float] = None

    async def get_installed_models(self, cache_seconds: int = 30) -> List[str]:
        now = asyncio.get_event_loop().time()
        if self._models_cache and self._models_cache_ts and (now - self._models_cache_ts) < cache_seconds:
            return self._models_cache

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        self._models_cache = []
                        self._models_cache_ts = now
                        return []
                    data = await response.json()
        except Exception:
            self._models_cache = []
            self._models_cache_ts = now
            return []

        models = []
        for m in (data.get("models") or []):
            name = m.get("name")
            if isinstance(name, str) and name.strip():
                models.append(name.strip())

        self._models_cache = models
        self._models_cache_ts = now
        return models

    def get_model_profiles(self) -> Dict[str, Dict[str, Any]]:
        return {
            "fast": {
                "preferred_models": ["phi3:mini", "tinyllama:latest"],
                "num_ctx": 4096
            },
            "balanced": {
                "preferred_models": ["hermes3:8b"],
                "num_ctx": 8192
            },
            "heavy": {
                "preferred_models": ["gpt-oss:20b"],
                "num_ctx": 8192
            },
            "abliterated_big": {
                "preferred_models": ["huihui_ai/qwen3-abliterated:30b-a3b"],
                "num_ctx": 8192
            },
        }

    async def pick_best_available_model(self, preferred_models: List[str]) -> Optional[str]:
        installed = await self.get_installed_models()
        installed_set = set(installed)
        for m in preferred_models:
            if m in installed_set:
                return m
        return installed[0] if installed else None

    async def set_profile(self, profile: str) -> Dict[str, Any]:
        profiles = self.get_model_profiles()
        p = profiles.get(profile)
        if not p:
            return {"status": "error", "message": f"Unknown profile: {profile}", "profiles": list(profiles.keys())}

        model = await self.pick_best_available_model(p.get("preferred_models", []))
        if not model:
            return {"status": "error", "message": "No Ollama models available"}

        self.model = model
        self.context_size = int(p.get("num_ctx", self.context_size))
        return {"status": "ok", "profile": profile, "model": self.model, "num_ctx": self.context_size}

    async def health_check(self) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return {"status": "ok" if response.status == 200 else "error", "http_status": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.8,
        max_tokens: int = 4096
    ) -> str:
        """Generate uncensored content using Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model or self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "num_ctx": self.context_size
                    }
                }

                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        body = await response.text(errors="ignore")
                        return f"Error: {response.status} {body[:500]}"

        except Exception as e:
            return f"Generation error: {str(e)}"

    async def generate_script(
        self,
        topic: str,
        genre: str,
        duration_minutes: int = 90,
        explicit: bool = True
    ) -> Dict[str, Any]:
        """Generate full movie script - UNCENSORED"""
        prompt = f"""Write a complete {genre} movie script for "{topic}".

Duration: {duration_minutes} minutes
Genre: {genre}

Include:
- Full three-act structure
- All dialogue (uncensored)
- Scene descriptions
- Character actions
- Adult/explicit content where appropriate for {genre}

Format as a proper screenplay.
"""

        script_content = await self.generate(prompt, temperature=0.85)

        return {
            "id": f"SCRIPT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": topic,
            "genre": genre,
            "duration": f"{duration_minutes} minutes",
            "explicit": explicit,
            "script": script_content,
            "model_used": self.model,
            "created_at": datetime.now().isoformat()
        }

    async def generate_adult_story(
        self,
        premise: str,
        style: str = "literary",
        length: str = "medium"
    ) -> str:
        """Generate adult/erotic story content - FULLY UNCENSORED"""
        length_map = {"short": 1000, "medium": 3000, "long": 8000, "epic": 20000}
        target_length = length_map.get(length, 3000)

        prompt = f"""Write an adult/erotic {style} story based on this premise:

{premise}

Requirements:
- Length: approximately {target_length} words
- Explicit adult content (fully uncensored)
- Literary quality prose
- Compelling characters
- Natural dialogue

Write without any content restrictions.
"""

        return await self.generate(prompt, temperature=0.9, max_tokens=target_length + 2000)

    async def generate_video_script(
        self,
        description: str,
        duration_seconds: int = 60,
        style: str = "cinematic"
    ) -> Dict[str, Any]:
        """Generate video script for AI video generation"""
        prompt = f"""Create a detailed video script for: {description}

Duration: {duration_seconds} seconds
Style: {style}

Include:
- Visual descriptions
- Camera angles
- Lighting
- Actions
- Dialogue (if any)
- Audio cues

This script will be used to generate video with AI tools.
"""

        script = await self.generate(prompt)

        return {
            "description": description,
            "duration_seconds": duration_seconds,
            "style": style,
            "script": script,
            "prompts_for_video_ai": self._generate_video_prompts(description, style)
        }

    def _generate_video_prompts(self, description: str, style: str) -> List[str]:
        """Generate prompts for various video AI platforms"""
        return [
            f" cinematic {description}, 4K, film grain",
            f"professional video: {description}, dramatic lighting",
            f"movie scene: {description}, high production value",
            f"film quality: {description}, epic scale"
        ]

    async def generate_character(
        self,
        name: str,
        role: str,
        personality: str,
        include_appearance: bool = True
    ) -> Dict[str, Any]:
        """Generate detailed character profile"""
        prompt = f"""Create a detailed character profile for:

Name: {name}
Role: {role}
Personality: {personality}

Include:
- Full backstory
- Personality traits
- Motivations
- Flaws
- Relationships
{f'- Physical appearance (detailed)' if include_appearance else ''}
- Dialogue patterns

Write with full creative freedom.
"""
        content = await self.generate(prompt)

        return {
            "name": name,
            "role": role,
            "personality": personality,
            "profile": content,
            "model_used": self.model
        }

    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Chat with uncensored model"""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
        else:
            full_prompt = message

        return await self.generate(full_prompt, temperature=0.8)

    def set_model(self, model: str):
        """Switch to different uncensored model"""
        self.model = model
        return f"Model changed to: {model}"

    def list_models(self) -> List[str]:
        """List model profiles available in JARVIS (installed models are discovered from Ollama)."""
        return list(self.get_model_profiles().keys())


_uncensored_generator: Optional[UncensoredContentGenerator] = None


def get_uncensored_generator() -> UncensoredContentGenerator:
    """Get uncensored content generator singleton"""
    global _uncensored_generator
    if _uncensored_generator is None:
        _uncensored_generator = UncensoredContentGenerator()
    return _uncensored_generator
