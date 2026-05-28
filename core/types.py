"""
JARVIS Ecosystem - Type Definitions
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from datetime import datetime


class AgentStatus(Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class AgentTier(Enum):
    TIER_0_DIRECTOR = 0
    TIER_1_GATEKEEPER = 1
    TIER_2_SPECIALIST = 2
    TIER_3_EXECUTOR = 3


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class MessageType(Enum):
    COMMAND = "command"
    TASK = "task"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    HEARTBEAT = "heartbeat"
    ALERT = "alert"


@dataclass
class AgentInfo:
    name: str
    tier: AgentTier
    role: str
    status: AgentStatus = AgentStatus.STANDBY
    capabilities: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    last_active: datetime = field(default_factory=datetime.now)
    stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    id: str
    msg_type: MessageType
    sender: str
    receiver: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)