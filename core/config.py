"""
JARVIS Ecosystem - Configuration
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json


@dataclass
class Config:
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    model: str = "gpt-4"
    voice_enabled: bool = True
    speech_to_text_model: str = "whisper-1"
    text_to_speech_model: str = "tts-1"

    log_level: str = "INFO"
    log_file: str = "jarvis.log"

    frontend_host: str = "localhost"
    frontend_port: int = 3000

    message_bus_host: str = "localhost"
    message_bus_port: int = 6379

    memory_db_path: str = "jarvis_memory.db"

    claude_code_path: Optional[str] = None

    max_concurrent_tasks: int = 10
    task_timeout_seconds: int = 300

    dashboard_stats_interval: int = 5

    def __post_init__(self):
        env_api_key = os.getenv("OPENAI_API_KEY")
        if env_api_key:
            self.openai_api_key = env_api_key

        env_anthropic = os.getenv("ANTHROPIC_API_KEY")
        if env_anthropic:
            self.anthropic_api_key = env_anthropic

        env_openrouter = os.getenv("OPENROUTER_API_KEY")
        if env_openrouter:
            self.openrouter_api_key = env_openrouter

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "voice_enabled": self.voice_enabled,
            "log_level": self.log_level,
            "frontend_host": self.frontend_host,
            "frontend_port": self.frontend_port,
        }

    @classmethod
    def load(cls, path: str) -> "Config":
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return cls(**data)
        return cls()

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)