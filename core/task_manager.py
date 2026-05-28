"""
JARVIS Ecosystem - Task Manager
Task creation, assignment, and tracking
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
from dataclasses import dataclass, field

from .types import Task, TaskStatus, TaskPriority, MessageType
from .message_bus import MessageBus


class TaskManager:
    """
    Manages all tasks in the JARVIS ecosystem.
    Handles task creation, assignment, tracking, and completion.
    """

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self._tasks: Dict[str, Task] = {}
        self._agent_tasks: Dict[str, List[str]] = defaultdict(list)
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._lock = asyncio.Lock()
        self._observers: List[Callable] = []

    async def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority,
        created_by: str,
        assigned_to: Optional[str] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Task:
        """Create a new task."""
        task = Task(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            priority=priority,
            created_by=created_by,
            assigned_to=assigned_to,
            parent_id=parent_id,
            metadata=metadata or {}
        )

        async with self._lock:
            self._tasks[task.id] = task
            if assigned_to:
                self._agent_tasks[assigned_to].append(task.id)

        await self._notify_observers("task_created", task)

        if assigned_to:
            await self._assign_task_to_agent(task)

        return task

    async def _assign_task_to_agent(self, task: Task):
        """Send task to the assigned agent."""
        await self.message_bus.send_message(
            msg_type=MessageType.TASK,
            sender="task_manager",
            receiver=task.assigned_to,
            content={
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "metadata": task.metadata
            },
            correlation_id=task.id
        )

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ) -> bool:
        """Update task status."""
        async with self._lock:
            if task_id not in self._tasks:
                return False

            task = self._tasks[task_id]
            task.status = status
            task.updated_at = datetime.now()

            if result is not None:
                task.result = result
            if error:
                task.error = error

        await self._notify_observers("task_updated", task)
        return True

    async def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        async with self._lock:
            if task_id not in self._tasks:
                return False

            task = self._tasks[task_id]

            if task.assigned_to:
                self._agent_tasks[task.assigned_to].remove(task_id)

            task.assigned_to = agent_id
            task.updated_at = datetime.now()
            self._agent_tasks[agent_id].append(task_id)

        await self._assign_task_to_agent(task)
        await self._notify_observers("task_assigned", task)
        return True

    async def add_subtask(
        self,
        parent_id: str,
        title: str,
        description: str,
        priority: TaskPriority,
        created_by: str,
        assigned_to: Optional[str] = None
    ) -> Optional[Task]:
        """Add a subtask to a parent task."""
        if parent_id not in self._tasks:
            return None

        subtask = await self.create_task(
            title=title,
            description=description,
            priority=priority,
            created_by=created_by,
            assigned_to=assigned_to,
            parent_id=parent_id
        )

        async with self._lock:
            self._tasks[parent_id].subtasks.append(subtask.id)

        return subtask

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    async def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """Get all tasks assigned to an agent."""
        task_ids = self._agent_tasks.get(agent_id, [])
        return [self._tasks[tid] for tid in task_ids if tid in self._tasks]

    async def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [t for t in self._tasks.values() if t.status == status]

    async def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get all tasks with a specific priority."""
        return [t for t in self._tasks.values() if t.priority == priority]

    async def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    async def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks sorted by priority."""
        pending = await self.get_tasks_by_status(TaskStatus.PENDING)
        return sorted(pending, key=lambda t: t.priority.value)

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]

        if task.assigned_to:
            self._agent_tasks[task.assigned_to].remove(task_id)

        del self._tasks[task_id]
        await self._notify_observers("task_deleted", {"id": task_id})
        return True

    async def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics."""
        tasks = list(self._tasks.values())
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in tasks if t.status == TaskStatus.FAILED]),
            "by_priority": {
                "critical": len([t for t in tasks if t.priority == TaskPriority.CRITICAL]),
                "high": len([t for t in tasks if t.priority == TaskPriority.HIGH]),
                "medium": len([t for t in tasks if t.priority == TaskPriority.MEDIUM]),
                "low": len([t for t in tasks if t.priority == TaskPriority.LOW])
            }
        }

    def add_observer(self, callback: Callable):
        """Add an observer for task events."""
        self._observers.append(callback)

    async def _notify_observers(self, event: str, data: Any):
        """Notify observers of task events."""
        for callback in self._observers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event, data)
                else:
                    callback(event, data)
            except Exception as e:
                print(f"Observer error: {e}")

    async def getKanbanBoard(self) -> Dict[str, List[Dict]]:
        """Get tasks organized as Kanban columns."""
        tasks = list(self._tasks.values())
        return {
            "todo": [
                {"id": t.id, "title": t.title, "priority": t.priority.name, "assigned_to": t.assigned_to}
                for t in tasks if t.status == TaskStatus.PENDING
            ],
            "in_progress": [
                {"id": t.id, "title": t.title, "priority": t.priority.name, "assigned_to": t.assigned_to}
                for t in tasks if t.status == TaskStatus.IN_PROGRESS
            ],
            "done": [
                {"id": t.id, "title": t.title, "priority": t.priority.name, "assigned_to": t.assigned_to}
                for t in tasks if t.status == TaskStatus.COMPLETED
            ]
        }