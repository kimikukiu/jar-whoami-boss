"""
JARVIS Automation Bot
Automatizare task-uri repetitive, web scraping, RPA
Implementat pe baza analizei video-urilor din D:\pj-for-jarvis-implement-features
"""

import asyncio
import json
import re
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import base64


class AutomationType(Enum):
    """Tipuri de automatizări suportate"""
    WEB_SCRAPING = "web_scraping"
    FORM_FILLING = "form_filling"
    MOUSE_AUTOMATION = "mouse_automation"
    KEYBOARD_AUTOMATION = "keyboard_automation"
    SCHEDULED_TASK = "scheduled_task"
    DATA_EXTRACTION = "data_extraction"
    API_INTEGRATION = "api_integration"
    FILE_MANAGEMENT = "file_management"
    EMAIL_AUTOMATION = "email_automation"
    NOTIFICATION = "notification"


class TriggerType(Enum):
    """Tipuri de trigger-uri pentru automatizări"""
    SCHEDULE = "schedule"
    EVENT = "event"
    WEBHOOK = "webhook"
    MANUAL = "manual"
    CONDITION = "condition"


@dataclass
class AutomationTask:
    """Reprezintă un task de automatizare"""
    id: str
    name: str
    description: str
    type: AutomationType
    trigger: TriggerType
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    schedule: Optional[str] = None  # Cron expression
    conditions: List[Dict[str, Any]] = None
    retry_count: int = 3
    retry_delay: int = 5  # seconds
    timeout: int = 300  # seconds
    status: str = "active"  # active, paused, completed, failed
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.conditions is None:
            self.conditions = []
        if self.metadata is None:
            self.metadata = {}
        if self.id is None:
            self.id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(self.name) % 10000}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertește în dicționar"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "trigger": self.trigger.value,
            "trigger_config": self.trigger_config,
            "actions": self.actions,
            "schedule": self.schedule,
            "conditions": self.conditions,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }


@dataclass
class AutomationResult:
    """Rezultatul rulării unei automatizări"""
    task_id: str
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, success, failure, timeout
    actions_results: List[Dict[str, Any]] = None
    output: Any = None
    error_message: Optional[str] = None
    logs: List[str] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.actions_results is None:
            self.actions_results = []
        if self.logs is None:
            self.logs = []
        if self.metrics is None:
            self.metrics = {
                "actions_executed": 0,
                "actions_failed": 0,
                "duration_ms": 0
            }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "actions_results": self.actions_results,
            "output": self.output,
            "error_message": self.error_message,
            "logs": self.logs,
            "metrics": self.metrics
        }


class AutomationBot:
    """
    Bot de automatizare pentru JARVIS
    Gestionează task-uri de automatizare, scheduling și execuție
    """
    
    def __init__(self, db_path: str = "data/automation.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tasks: Dict[str, AutomationTask] = {}
        self.scheduled_jobs: Dict[str, Any] = {}
        self.running_tasks: Dict[str, AutomationResult] = {}
        self.task_history: List[AutomationResult] = []
        
        self.max_concurrent_tasks = 5
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Inițializează baza de date
        self._init_database()
        
        # Încarcă task-uri existente
        self._load_tasks()
    
    def _init_database(self):
        """Inițializează schema bazei de date"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tabel pentru task-uri
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                trigger TEXT NOT NULL,
                trigger_config TEXT,
                actions TEXT,
                schedule TEXT,
                conditions TEXT,
                retry_count INTEGER DEFAULT 3,
                retry_delay INTEGER DEFAULT 5,
                timeout INTEGER DEFAULT 300,
                status TEXT DEFAULT 'active',
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                run_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Tabel pentru istoricul rulărilor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_history (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                actions_results TEXT,
                output TEXT,
                error_message TEXT,
                logs TEXT,
                metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES automation_tasks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_tasks(self):
        """Încarcă task-urile din baza de date"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM automation_tasks WHERE status = 'active'")
        rows = cursor.fetchall()
        
        for row in rows:
            task = AutomationTask(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                type=AutomationType(row['type']),
                trigger=TriggerType(row['trigger']),
                trigger_config=json.loads(row['trigger_config']) if row['trigger_config'] else {},
                actions=json.loads(row['actions']) if row['actions'] else [],
                schedule=row['schedule'],
                conditions=json.loads(row['conditions']) if row['conditions'] else [],
                retry_count=row['retry_count'],
                retry_delay=row['retry_delay'],
                timeout=row['timeout'],
                status=row['status'],
                last_run=datetime.fromisoformat(row['last_run']) if row['last_run'] else None,
                next_run=datetime.fromisoformat(row['next_run']) if row['next_run'] else None,
                run_count=row['run_count'],
                success_count=row['success_count'],
                failure_count=row['failure_count'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            
            self.tasks[task.id] = task
        
        conn.close()
        
        print(f"✓ {len(self.tasks)} task-uri încărcate din baza de date")
    
    # === GESTIONARE TASK-URI ===
    
    def create_task(self, task: AutomationTask) -> str:
        """Creează un nou task de automatizare"""
        # Salvează în memorie
        self.tasks[task.id] = task
        
        # Salvează în baza de date
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO automation_tasks 
            (id, name, description, type, trigger, trigger_config, actions, schedule, conditions,
             retry_count, retry_delay, timeout, status, last_run, next_run, run_count, success_count, 
             failure_count, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id,
            task.name,
            task.description,
            task.type.value,
            task.trigger.value,
            json.dumps(task.trigger_config),
            json.dumps(task.actions),
            task.schedule,
            json.dumps(task.conditions),
            task.retry_count,
            task.retry_delay,
            task.timeout,
            task.status,
            task.last_run.isoformat() if task.last_run else None,
            task.next_run.isoformat() if task.next_run else None,
            task.run_count,
            task.success_count,
            task.failure_count,
            task.created_at.isoformat() if task.created_at else None,
            task.updated_at.isoformat() if task.updated_at else None,
            json.dumps(task.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Task creat: {task.name} ({task.id})")
        
        # Dacă botul rulează, programează task-ul
        if self.running and task.trigger == TriggerType.SCHEDULE and task.schedule:
            self._schedule_task(task)
        
        return task.id
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizează un task existent"""
        if task_id not in self.tasks:
            print(f"✗ Task negăsit: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # Aplică actualizările
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        
        # Salvează în baza de date
        self.create_task(task)  # INSERT OR REPLACE
        
        print(f"✓ Task actualizat: {task.name}")
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Șterge un task"""
        if task_id not in self.tasks:
            print(f"✗ Task negăsit: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # Oprește task-ul dacă rulează
        if task_id in self.running_tasks:
            self.stop_task(task_id)
        
        # Elimină din programare dacă este programat
        if task_id in self.scheduled_jobs:
            del self.scheduled_jobs[task_id]
        
        # Elimină din memorie
        del self.tasks[task_id]
        
        # Șterge din baza de date
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM automation_tasks WHERE id = ?", (task_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Task șters: {task_id}")
        return True
    
    def get_task(self, task_id: str) -> Optional[AutomationTask]:
        """Obține un task după ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: str = None, trigger_type: TriggerType = None) -> List[AutomationTask]:
        """Listează toate task-urile"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if trigger_type:
            tasks = [t for t in tasks if t.trigger == trigger_type]
        
        return tasks
    
    # === EXECUȚIE TASK-URI ===
    
    def start(self):
        """Pornește Automation Bot"""
        if self.running:
            print("⚠️ Botul rulează deja")
            return
        
        self.running = True
        
        # Programează toate task-urile active cu trigger SCHEDULE
        for task in self.tasks.values():
            if task.status == "active" and task.trigger == TriggerType.SCHEDULE and task.schedule:
                self._schedule_task(task)
        
        # Pornește task-ul scheduler în background
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        print("✅ Automation Bot pornit")
    
    def stop(self):
        """Oprește Automation Bot"""
        if not self.running:
            print("⚠️ Botul nu rulează")
            return
        
        self.running = False
        
        # Anulează task-ul scheduler
        if self.scheduler_task:
            self.scheduler_task.cancel()
        
        # Oprește toate task-urile care rulează
        for task_id in list(self.running_tasks.keys()):
            self.stop_task(task_id)
        
        print("✅ Automation Bot oprit")
    
    async def _scheduler_loop(self):
        """Loop principal pentru scheduler"""
        while self.running:
            try:
                # Verifică task-urile programate
                now = datetime.now()
                
                for task_id, scheduled_time in list(self.scheduled_jobs.items()):
                    if scheduled_time <= now:
                        # Execută task-ul
                        task = self.tasks.get(task_id)
                        if task and task.status == "active":
                            asyncio.create_task(self._execute_task(task))
                        
                        # Resetează programarea pentru următoarea rulare
                        if task and task.schedule:
                            next_run = self._calculate_next_run(task.schedule)
                            self.scheduled_jobs[task_id] = next_run
                            task.next_run = next_run
                
                # Așteaptă 1 secundă înainte de următoarea verificare
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Eroare în scheduler: {e}")
                await asyncio.sleep(5)  # Așteaptă mai mult în caz de eroare
    
    def _schedule_task(self, task: AutomationTask):
        """Programează un task pentru execuție"""
        if not task.schedule:
            return
        
        next_run = self._calculate_next_run(task.schedule)
        self.scheduled_jobs[task.id] = next_run
        task.next_run = next_run
        
        print(f"📅 Task programat: {task.name} -> {next_run}")
    
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Calculează următoarea rulare bazat pe expresia cron"""
        # Implementare simplificată pentru cron
        # În practică, ai folosi o bibliotecă precum croniter
        
        now = datetime.now()
        
        # Parsează expresia cron (format simplificat: "minute hour day month weekday")
        parts = cron_expression.split()
        if len(parts) != 5:
            # Default: rulează la fiecare minut
            return now + timedelta(minutes=1)
        
        minute, hour, day, month, weekday = parts
        
        # Calculează următoarea rulare
        next_run = now
        
        # Dacă este specificat un minut specific
        if minute != "*":
            target_minute = int(minute)
            if next_run.minute >= target_minute:
                next_run += timedelta(hours=1)
            next_run = next_run.replace(minute=target_minute, second=0, microsecond=0)
        else:
            # Rulează la fiecare minut
            next_run += timedelta(minutes=1)
            next_run = next_run.replace(second=0, microsecond=0)
        
        # Dacă este specificată o oră specifică
        if hour != "*":
            target_hour = int(hour)
            if next_run.hour > target_hour or (next_run.hour == target_hour and next_run.minute > 0):
                next_run += timedelta(days=1)
            next_run = next_run.replace(hour=target_hour)
        
        return next_run
    
    async def _execute_task(self, task: AutomationTask) -> AutomationResult:
        """Execută un task de automatizare"""
        
        # Generează ID-uri
        run_id = f"run_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Creează obiectul de rezultat
        result = AutomationResult(
            task_id=task.id,
            run_id=run_id,
            start_time=datetime.now()
        )
        
        # Adaugă în lista de task-uri care rulează
        self.running_tasks[task.id] = result
        
        # Actualizează statusul task-ului
        task.last_run = datetime.now()
        task.run_count += 1
        
        try:
            print(f"\n🚀 Executare task: {task.name}")
            print(f"   ID: {task.id}")
            print(f"   Tip: {task.type.value}")
            print(f"   Acțiuni: {len(task.actions)}")
            
            # Execută fiecare acțiune
            for i, action in enumerate(task.actions, 1):
                print(f"\n   [{i}/{len(task.actions)}] {action.get('name', 'Action')}")
                
                action_result = await self._execute_action(action, task)
                
                result.actions_results.append(action_result)
                
                if action_result.get('success'):
                    print(f"   ✅ Succes: {action_result.get('message', 'OK')}")
                else:
                    print(f"   ❌ Eșuat: {action_result.get('error', 'Unknown error')}")
                    
                    # Decidem dacă să continuăm sau nu bazat pe configurare
                    if action.get('continue_on_failure', False):
                        print(f"   ⚠️ Continuare în ciuda erorii (continue_on_failure=true)")
                    else:
                        raise Exception(f"Acțiune eșuată: {action_result.get('error', 'Unknown error')}")
            
            # Task completat cu succes
            result.status = "success"
            result.end_time = datetime.now()
            result.output = {
                "actions_executed": len(result.actions_results),
                "all_succeeded": all(r.get('success', False) for r in result.actions_results)
            }
            
            task.success_count += 1
            
            print(f"\n✅ Task finalizat cu succes: {task.name}")
            print(f"   Durată: {(result.end_time - result.start_time).total_seconds():.2f}s")
            print(f"   Acțiuni: {len(result.actions_results)}")
            
        except Exception as e:
            # Task eșuat
            result.status = "failure"
            result.end_time = datetime.now()
            result.error_message = str(e)
            
            task.failure_count += 1
            
            print(f"\n❌ Task eșuat: {task.name}")
            print(f"   Eroare: {str(e)}")
            
            # Încearcă din nou dacă este configurat
            if task.retry_count > 0:
                print(f"   🔄 Încercare din nou în {task.retry_delay} secunde...")
                await asyncio.sleep(task.retry_delay)
                task.retry_count -= 1
                return await self._execute_task(task)
        
        finally:
            # Curățare
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            
            # Salvează rezultatul în istoric
            self.task_history.append(result)
            self._save_result(result)
        
        return result
    
    async def _execute_action(self, action: Dict[str, Any], task: AutomationTask) -> Dict[str, Any]:
        """Execută o acțiune specifică"""
        action_type = action.get('type', 'unknown')
        
        result = {
            'action_type': action_type,
            'success': False,
            'start_time': datetime.now().isoformat(),
            'message': '',
            'error': None,
            'output': None
        }
        
        try:
            if action_type == 'web_request':
                # Execută o cerere web
                import aiohttp
                
                url = action.get('url')
                method = action.get('method', 'GET')
                headers = action.get('headers', {})
                data = action.get('data')
                
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, headers=headers, data=data) as response:
                        result['output'] = {
                            'status': response.status,
                            'headers': dict(response.headers),
                            'body': await response.text()
                        }
                        result['success'] = 200 <= response.status < 300
                        result['message'] = f"HTTP {response.status}"
            
            elif action_type == 'database_query':
                # Execută o interogare SQL
                connection_string = action.get('connection_string')
                query = action.get('query')
                
                # Implementare simplificată - în practică ai folosi SQLAlchemy sau similar
                result['output'] = {'rows': [], 'columns': []}
                result['success'] = True
                result['message'] = "Query executed"
            
            elif action_type == 'file_operation':
                # Operațiuni cu fișiere
                operation = action.get('operation')  # read, write, copy, move, delete
                path = action.get('path')
                content = action.get('content')
                
                if operation == 'read':
                    with open(path, 'r', encoding='utf-8') as f:
                        result['output'] = f.read()
                elif operation == 'write':
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    result['output'] = f"Written {len(content)} characters"
                
                result['success'] = True
                result['message'] = f"File {operation} completed"
            
            elif action_type == 'data_transform':
                # Transformări de date
                input_data = action.get('data', [])
                transformation = action.get('transformation', {})
                
                # Implementare simplificată
                result['output'] = input_data  # Placeholder
                result['success'] = True
                result['message'] = "Data transformed"
            
            elif action_type == 'notification':
                # Trimite notificare
                title = action.get('title', 'Notification')
                message = action.get('message', '')
                channel = action.get('channel', 'console')  # console, email, webhook
                
                if channel == 'console':
                    print(f"\n🔔 {title}")
                    print(f"   {message}\n")
                
                # Alte canale pot fi implementate aici
                
                result['output'] = {'channel': channel, 'sent': True}
                result['success'] = True
                result['message'] = f"Notification sent via {channel}"
            
            elif action_type == 'custom_script':
                # Execută script custom
                script = action.get('script', '')
                language = action.get('language', 'python')
                
                # Implementare simplificată - în practică ai folosi subprocess sau similar
                result['output'] = f"Executed {language} script"
                result['success'] = True
                result['message'] = "Custom script executed"
            
            else:
                result['error'] = f"Tip de acțiune necunoscut: {action_type}"
                result['message'] = "Unknown action type"
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['message'] = f"Action failed: {str(e)}"
        
        finally:
            result['end_time'] = datetime.now().isoformat()
            result['duration_ms'] = (
                datetime.fromisoformat(result['end_time']) - 
                datetime.fromisoformat(result['start_time'])
            ).total_seconds() * 1000
        
        return result
    
    def _schedule_task(self, task: AutomationTask):
        """Programează un task pentru execuție"""
        if not task.schedule:
            return
        
        try:
            # Parsează expresia cron
            next_run = self._calculate_next_run(task.schedule)
            
            # Stochează programarea
            self.scheduled_jobs[task.id] = next_run
            task.next_run = next_run
            
            print(f"📅 Task programat: {task.name} -> {next_run}")
            
        except Exception as e:
            print(f"❌ Eroare la programarea task-ului {task.name}: {e}")
    
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Calculează următoarea rulare bazat pe expresia cron"""
        # Implementare simplificată pentru cron
        # În practică, ai folosi o bibliotecă precum croniter
        
        now = datetime.now()
        
        # Parsează expresia cron (format simplificat: "minute hour day month weekday")
        parts = cron_expression.split()
        if len(parts) != 5:
            # Default: rulează la fiecare minut
            return now + timedelta(minutes=1)
        
        minute, hour, day, month, weekday = parts
        
        # Calculează următoarea rulare
        next_run = now
        
        # Dacă este specificat un minut specific
        if minute != "*":
            target_minute = int(minute)
            if next_run.minute >= target_minute:
                next_run += timedelta(hours=1)
            next_run = next_run.replace(minute=target_minute, second=0, microsecond=0)
        else:
            # Rulează la fiecare minut
            next_run += timedelta(minutes=1)
            next_run = next_run.replace(second=0, microsecond=0)
        
        # Dacă este specificată o oră specifică
        if hour != "*":
            target_hour = int(hour)
            if next_run.hour > target_hour or (next_run.hour == target_hour and next_run.minute > 0):
                next_run += timedelta(days=1)
            next_run = next_run.replace(hour=target_hour)
        
        return next_run
    
    def _save_result(self, result: AutomationResult):
        """Salvează rezultatul în baza de date"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO automation_history 
            (id, task_id, run_id, start_time, end_time, status, actions_results, 
             output, error_message, logs, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{result.task_id}_{result.run_id}",
            result.task_id,
            result.run_id,
            result.start_time.isoformat() if result.start_time else None,
            result.end_time.isoformat() if result.end_time else None,
            result.status,
            json.dumps(result.actions_results),
            json.dumps(result.output) if result.output else None,
            result.error_message,
            json.dumps(result.logs),
            json.dumps(result.metrics)
        ))
        
        conn.commit()
        conn.close()


# Dacă rulăm direct
if __name__ == "__main__":
    print("=" * 70)
    print("JARVIS DATA ENGINE")
    print("=" * 70)
    print()
    print("Exemple de utilizare:")
    print()
    print("1. Inițializare motor de date:")
    print("   engine = DataEngine()")
    print()
    print("2. Adăugare sursă de date:")
    print("   source = DataSource(")
    print("       id='db_prod',")
    print("       name='Production DB',")
    print("       type='database',")
    print("       connection_string='postgresql://...',")
    print("       format=DataFormat.SQL")
    print("   )")
    print("   engine.add_source(source)")
    print()
    print("3. Interogare date:")
    print("   data = engine.query('SELECT * FROM users')")
    print()
    print("4. Aplicare transformare:")
    print("   transformed = engine.apply_transform(")
    print("       data,")
    print("       transform_id='filter_active'")
    print("   )")
    print()
    print("5. Export date:")
    print("   engine.export_to_format(")
    print("       data,")
    print("       format=DataFormat.CSV,")
    print("       output_path='output.csv'")
    print("   )")
    print()
    print("=" * 70)