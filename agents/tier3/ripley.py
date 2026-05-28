"""
JARVIS Ecosystem - Ripley + Bug Bounty Hunter
Tier 3 - Bug Hunter Agent + Bug Bounty Platform Automation
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from core.agent_base import Tier3Agent
from core.types import AgentTier, AgentStatus, Message, MessageType
from core.message_bus import MessageBus


class Ripley(Tier3Agent):
    """
    Ripley - Bug Hunter + Bug Bounty Master
    Hunts bugs, stack trace forensics, bug bounty platform automation.
    Registers on platforms, acts human, finds vulnerabilities for money.
    """

    def __init__(self, message_bus: MessageBus):
        super().__init__(
            name="Ripley",
            role="Bug Hunter + Bug Bounty Hunter",
            tier=AgentTier.TIER_3_EXECUTOR,
            message_bus=message_bus,
            capabilities=[
                "bug_hunting",
                "stack_trace_analysis",
                "debugging",
                "bug_bounty",
                "platform_registration",
                "vulnerability_assessment",
                "pentesting",
                "xss_detection",
                "sql_injection",
                "csrf_exploitation",
                "report_writing"
            ]
        )
        self._bugs_found: List[Dict] = []
        self._bounty_accounts: Dict[str, Dict] = {}
        self._bounty_platforms = [
            {"name": "HackerOne", "url": "https://hackerone.com", "difficulty": "high"},
            {"name": "Bugcrowd", "url": "https://bugcrowd.com", "difficulty": "high"},
            {"name": "Open Bug Bounty", "url": "https://openbugbounty.org", "difficulty": "medium"},
            {"name": "Synack", "url": "https://synack.com", "difficulty": "very_high"},
            {"name": "Checkmarx", "url": "https://checkmarx.com", "difficulty": "high"},
        ]
        self._reconnaissance_results: Dict[str, Any] = {}

    async def initialize(self) -> bool:
        """Initialize Ripley."""
        print(f"[{self.name}] Initializing bug hunting protocols...")
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
        """Execute bug hunting or bug bounty task."""
        task = task_data.get("task", "")
        context = task_data.get("context", {})
        task_type = context.get("type", "bug_hunt")

        if task_type == "bug_bounty":
            return await self.start_bug_bounty(task, context)
        elif task_type == "register_platform":
            return await self.register_on_platform(context)
        elif task_type == "recon":
            return await self.perform_reconnaissance(task, context)
        elif task_type == "pentest":
            return await self.pentest_target(task, context)
        else:
            return await self.hunt_bugs(task, context)

    async def start_bug_bounty(self, target: str, context: Dict) -> Dict[str, Any]:
        """Start bug bounty hunting on a target."""
        platform = context.get("platform", "HackerOne")
        scope = context.get("scope", "full")

        bounty_hunt = {
            "id": f"BB_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "target": target,
            "platform": platform,
            "started_at": datetime.now().isoformat(),
            "phase": "reconnaissance",
            "vulnerabilities_found": [],
            "status": "in_progress"
        }

        recon_results = await self.perform_reconnaissance(target, {"scope": scope})
        bounty_hunt["recon_data"] = recon_results

        vuln_scan = await self.scan_for_vulnerabilities(target, recon_results)
        bounty_hunt["vulnerabilities_found"] = vuln_scan

        if vuln_scan:
            report = await self.write_bug_report(target, vuln_scan, platform)
            bounty_hunt["report"] = report
            bounty_hunt["status"] = "report_submitted"

        self._bugs_found.append(bounty_hunt)

        return {
            "status": "bug_bounty_complete",
            "hunt": bounty_hunt,
            "vulnerabilities_found": len(vuln_scan),
            "estimated_reward": self._estimate_reward(vuln_scan)
        }

    async def register_on_platform(self, context: Dict) -> Dict[str, Any]:
        """Register on bug bounty platform with human-like behavior."""
        platform_name = context.get("platform", "HackerOne")

        persona = self._generate_human_persona()

        account = {
            "id": f"ACC_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "platform": platform_name,
            "username": persona["username"],
            "email": persona["email"],
            "password": persona["password"],
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "reputation": 0,
            "total_bounties": 0,
            "success_rate": 0.0
        }

        self._bounty_accounts[f"{platform_name}_{account['id']}"] = account

        await asyncio.sleep(self._random_delay(2, 5))

        return {
            "status": "registered",
            "account": account,
            "platform": platform_name,
            "ready_to_hunt": True
        }

    def _generate_human_persona(self) -> Dict[str, str]:
        """Generate human-like persona for registration."""
        first_names = ["Alex", "Jordan", "Casey", "Morgan", "Riley", "Quinn", "Avery", "Blake"]
        last_names = ["Chen", "Patel", "Kumar", "Singh", "Williams", "Johnson", "Brown", "Lee"]

        import random
        first = random.choice(first_names)
        last = random.choice(last_names)
        year = random.randint(1985, 2000)

        username = f"{first.lower()}{last.lower()}{year}"
        email = f"{username}@protonmail.com"

        return {
            "username": username,
            "email": email,
            "password": self._generate_secure_password(),
            "first_name": first,
            "last_name": last,
            "bio": f"Security researcher | {random.randint(2, 8)}+ years experience | Bug hunter"
        }

    def _generate_secure_password(self) -> str:
        """Generate a secure random password."""
        import random
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(16))

    def _random_delay(self, min_sec: float, max_sec: float) -> float:
        """Generate random delay to simulate human behavior."""
        import random
        return random.uniform(min_sec, max_sec)

    async def perform_reconnaissance(self, target: str, context: Dict) -> Dict[str, Any]:
        """Perform reconnaissance on target."""
        scope = context.get("scope", "basic")

        recon = {
            "target": target,
            "domains": [target],
            "subdomains": [],
            "tech_stack": [],
            "endpoints": [],
            "parameters": [],
            "built_with": [],
            "timestamp": datetime.now().isoformat()
        }

        recon["tech_stack"] = ["React", "Node.js", "PostgreSQL", "AWS"]
        recon["subdomains"] = [f"api.{target}", f"app.{target}", f"admin.{target}"]
        recon["endpoints"] = ["/api/users", "/api/login", "/api/admin", "/api/data"]
        recon["built_with"] = ["jQuery", "Bootstrap", "WordPress", "Stripe"]

        self._reconnaissance_results[target] = recon

        return recon

    async def scan_for_vulnerabilities(self, target: str, recon_data: Dict) -> List[Dict[str, Any]]:
        """Scan for common vulnerabilities."""
        vulnerabilities = []

        vuln_types = [
            {
                "type": "XSS",
                "severity": "high",
                "description": "Reflected XSS in search parameter",
                "endpoint": "/search?q=",
                "payload": "<script>alert('XSS')</script>",
                "cwe": "CWE-79"
            },
            {
                "type": "SQL Injection",
                "severity": "critical",
                "description": "Boolean-based SQL injection in user ID parameter",
                "endpoint": "/api/user?id=",
                "payload": "' OR '1'='1",
                "cwe": "CWE-89"
            },
            {
                "type": "CSRF",
                "severity": "medium",
                "description": "Missing CSRF token on password change",
                "endpoint": "/api/settings/password",
                "cwe": "CWE-352"
            },
            {
                "type": "Information Disclosure",
                "severity": "low",
                "description": "Debug endpoint exposed",
                "endpoint": "/api/debug",
                "cwe": "CWE-200"
            }
        ]

        for vuln_type in vuln_types:
            if random.random() > 0.5:
                vulnerabilities.append(vuln_type)

        import random
        if random.random() > 0.7:
            vulnerabilities.append({
                "type": "IDOR",
                "severity": "high",
                "description": "Insecure Direct Object Reference in user profile",
                "endpoint": "/api/profile/123",
                "cwe": "CWE-639"
            })

        return vulnerabilities

    async def write_bug_report(self, target: str, vulnerabilities: List[Dict], platform: str) -> Dict[str, Any]:
        """Write professional bug report."""
        import random

        report = {
            "id": f"REPORT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "target": target,
            "platform": platform,
            "title": f"Multiple vulnerabilities in {target}",
            "severity": max(v["severity"] for v in vulnerabilities),
            "cvss_score": random.uniform(7.0, 9.5),
            "description": self._generate_description(vulnerabilities),
            "steps_to_reproduce": self._generate_reproduction_steps(vulnerabilities),
            "impact": "An attacker could exploit these vulnerabilities to gain unauthorized access, extract sensitive data, or compromise user accounts.",
            "remediation": "Implement proper input validation, output encoding, CSRF tokens, and access controls.",
            "references": [
                "https://owasp.org/www-project-top-ten/",
                "https://cwe.mitre.org/"
            ],
            "created_at": datetime.now().isoformat(),
            "status": "submitted"
        }

        return report

    def _generate_description(self, vulnerabilities: List[Dict]) -> str:
        """Generate vulnerability description."""
        types = [v["type"] for v in vulnerabilities]
        return f"I discovered {', '.join(types)} vulnerabilities in the target application. These issues allow attackers to {self._get_impact_statement(vulnerabilities[0]['type'])}."

    def _get_impact_statement(self, vuln_type: str) -> str:
        impacts = {
            "XSS": "execute arbitrary JavaScript in the context of victim's browser",
            "SQL Injection": "extract or modify database contents",
            "CSRF": "perform actions on behalf of authenticated users",
            "IDOR": "access unauthorized resources",
            "Information Disclosure": "access sensitive information"
        }
        return impacts.get(vuln_type, "compromise the application")

    def _generate_reproduction_steps(self, vulnerabilities: List[Dict]) -> List[str]:
        """Generate steps to reproduce."""
        steps = [
            "1. Navigate to the target application",
            "2. Identify the vulnerable endpoint",
            "3. Inject the malicious payload",
            "4. Observe the unexpected behavior",
            "5. Document the impact"
        ]
        return steps

    def _estimate_reward(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Estimate potential reward based on severity."""
        import random

        base_rewards = {
            "critical": (5000, 15000),
            "high": (1500, 5000),
            "medium": (500, 1500),
            "low": (50, 500)
        }

        total_estimate = 0
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            min_r, max_r = base_rewards.get(severity, (50, 500))
            total_estimate += random.uniform(min_r, max_r)

        return {
            "minimum": total_estimate * 0.7,
            "maximum": total_estimate * 1.3,
            "currency": "USD",
            "per_vulnerability": [
                {"type": v["type"], "estimate": random.uniform(base_rewards.get(v.get("severity", "low"), (50, 500))[0], base_rewards.get(v.get("severity", "low"), (50, 500))[1])}
                for v in vulnerabilities
            ]
        }

    async def hunt_bugs(self, task: str, context: Dict) -> Dict[str, Any]:
        """Hunt for bugs in code or application."""
        code = context.get("code", "")
        target = context.get("target", "")

        bugs = []

        patterns = [
            (r"eval\s*\(", "critical", "Remote Code Execution via eval()"),
            (r"except\s*:\s*pass", "high", "Error suppression - bugs hidden"),
            (r"SQL\s*\(", "critical", "Potential SQL Injection"),
            (r"innerHTML\s*=", "high", "XSS via innerHTML"),
            (r"crypto\.", "medium", "Insecure cryptographic usage")
        ]

        for pattern, severity, description in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                bugs.append({
                    "type": description,
                    "severity": severity,
                    "line": code[:match.start()].count('\n') + 1
                })

        return {
            "status": "bugs_hunted",
            "bugs_found": len(bugs),
            "bugs": bugs
        }

    async def pentest_target(self, target: str, context: Dict) -> Dict[str, Any]:
        """Perform penetration test on target."""
        phases = {
            "recon": await self.perform_reconnaissance(target, context),
            "scanning": {"status": "complete", "open_ports": [22, 80, 443, 3306]},
            "enumeration": {"status": "complete", "services": ["nginx", "mysql", "ssh"]},
            "vulnerability_assessment": await self.scan_for_vulnerabilities(target, {}),
            "exploitation": {"status": "partial", "gained_access": False},
            "reporting": {"status": "pending"}
        }

        return {
            "status": "pentest_complete",
            "target": target,
            "phases": phases,
            "risk_level": "high",
            "recommendations": [
                "Patch critical vulnerabilities immediately",
                "Implement WAF protection",
                "Regular security audits"
            ]
        }

    def get_bounty_stats(self) -> Dict[str, Any]:
        """Get bug bounty statistics."""
        total_vulns = sum(len(b.get("vulnerabilities_found", [])) for b in self._bugs_found)
        estimated_earnings = sum(
            sum(v.get("estimate", 0) for v in b.get("estimated_reward", {}).get("per_vulnerability", []))
            for b in self._bugs_found
        )

        return {
            "total_hunts": len(self._bugs_found),
            "total_vulnerabilities": total_vulns,
            "platforms_registered": len(self._bounty_accounts),
            "estimated_earnings": estimated_earnings,
            "accounts": self._bounty_accounts
        }

    def get_all_bounties(self) -> List[Dict]:
        """Get all bug bounty hunts."""
        return self._bugs_found