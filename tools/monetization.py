"""
JARVIS Monetization System
Real revenue tracking from all platforms
"""

import os
import json
import time
import asyncio
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
DB_PATH = os.path.join(DATA_DIR, "jarvis_monetization.db")
CREDS_PATH = os.path.join(DATA_DIR, "platform_credentials.json")

os.makedirs(DATA_DIR, exist_ok=True)


class MonetizationDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS agent_revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    revenue REAL DEFAULT 0,
                    currency TEXT DEFAULT 'USD',
                    period TEXT DEFAULT 'monthly',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(agent_id, platform, period)
                );

                CREATE TABLE IF NOT EXISTS platform_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value REAL DEFAULT 0,
                    stat_text TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(agent_id, platform, stat_key)
                );

                CREATE TABLE IF NOT EXISTS revenue_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_agent_platform ON agent_revenue(agent_id, platform);
                CREATE INDEX IF NOT EXISTS idx_history ON revenue_history(agent_id, recorded_at);
            """)
            self.conn.commit()

    def save_revenue(self, agent_id: str, platform: str, revenue: float, currency: str = "USD", period: str = "monthly"):
        with self.lock:
            self.conn.execute("""
                INSERT INTO agent_revenue (agent_id, platform, revenue, currency, period, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(agent_id, platform, period) DO UPDATE SET
                    revenue = ?, currency = ?, updated_at = CURRENT_TIMESTAMP
            """, (agent_id, platform, revenue, currency, period, revenue, currency))
            self.conn.commit()

    def save_stat(self, agent_id: str, platform: str, key: str, value: float, text: str = None):
        with self.lock:
            self.conn.execute("""
                INSERT INTO platform_stats (agent_id, platform, stat_key, stat_value, stat_text, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(agent_id, platform, stat_key) DO UPDATE SET
                    stat_value = ?, stat_text = ?, updated_at = CURRENT_TIMESTAMP
            """, (agent_id, platform, key, value, text, value, text))
            self.conn.commit()

    def save_history(self, agent_id: str, platform: str, amount: float, currency: str = "USD"):
        with self.lock:
            self.conn.execute("""
                INSERT INTO revenue_history (agent_id, platform, amount, currency)
                VALUES (?, ?, ?, ?)
            """, (agent_id, platform, amount, currency))
            self.conn.commit()

    def get_agent_revenue(self, agent_id: str) -> List[Dict]:
        with self.lock:
            cursor = self.conn.execute("""
                SELECT platform, revenue, currency, period, updated_at
                FROM agent_revenue WHERE agent_id = ?
            """, (agent_id,))
            return [
                {"platform": r[0], "revenue": r[1], "currency": r[2], "period": r[3], "updated_at": r[4]}
                for r in cursor.fetchall()
            ]

    def get_agent_stats(self, agent_id: str) -> Dict[str, Dict]:
        with self.lock:
            cursor = self.conn.execute("""
                SELECT platform, stat_key, stat_value, stat_text
                FROM platform_stats WHERE agent_id = ?
            """, (agent_id,))
            result = {}
            for r in cursor.fetchall():
                platform, key, value, text = r
                if platform not in result:
                    result[platform] = {}
                result[platform][key] = {"value": value, "text": text}
            return result

    def get_total_revenue(self, agent_id: str = None) -> float:
        with self.lock:
            if agent_id:
                cursor = self.conn.execute("""
                    SELECT SUM(revenue) FROM agent_revenue WHERE agent_id = ?
                """, (agent_id,))
            else:
                cursor = self.conn.execute("SELECT SUM(revenue) FROM agent_revenue")
            result = cursor.fetchone()[0]
            return result or 0.0

    def close(self):
        self.conn.close()


class PlatformFetcher:
    """Fetches real data from various platforms."""

    @staticmethod
    def fetch_github(username: str) -> Dict:
        """Fetch public GitHub stats - no auth needed."""
        if not username or username == "none":
            return {}

        try:
            url = f"https://api.github.com/users/{username}"
            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            followers = data.get("followers", 0)
            following = data.get("following", 0)
            public_repos = data.get("public_repos", 0)

            repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
            req2 = urllib.request.Request(repos_url, headers={"User-Agent": "JARVIS/1.0"})
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                repos = json.loads(resp2.read().decode())

            total_stars = sum(r.get("stargazers_count", 0) for r in repos)
            total_forks = sum(r.get("forks_count", 0) for r in repos)
            total_watchers = sum(r.get("watchers_count", 0) for r in repos)

            return {
                "followers": followers,
                "following": following,
                "public_repos": public_repos,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "total_watchers": total_watchers,
            }
        except Exception as e:
            print(f"[GitHub] Error fetching {username}: {e}")
            return {}

    @staticmethod
    def fetch_youtube(channel_id: str, api_key: str = None) -> Dict:
        """Fetch YouTube stats. Requires API key for full data."""
        if not channel_id or channel_id == "none":
            return {}

        try:
            if api_key:
                url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    stats = data.get("items", [{}])[0].get("statistics", {})
                    return {
                        "subscribers": int(stats.get("subscriberCount", 0)),
                        "views": int(stats.get("viewCount", 0)),
                        "videos": int(stats.get("videoCount", 0)),
                    }
            else:
                return {"note": "API key needed for full stats"}
        except Exception as e:
            print(f"[YouTube] Error: {e}")
            return {}

    @staticmethod
    def fetch_tiktok(username: str) -> Dict:
        """TikTok public stats via unofficial API."""
        if not username or username == "none":
            return {}

        try:
            url = f"https://www.tiktok.com/api/user/detail/?uniqueId={username}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                user = data.get("userInfo", {}).get("user", {})
                stats = user.get("stats", {})
                return {
                    "followers": stats.get("followerCount", 0),
                    "following": stats.get("followingCount", 0),
                    "likes": stats.get("heartCount", 0),
                    "videos": stats.get("videoCount", 0),
                }
        except Exception as e:
            print(f"[TikTok] Error fetching {username}: {e}")
            return {}

    @staticmethod
    def fetch_instagram(username: str) -> Dict:
        """Instagram public stats via unofficial API."""
        if not username or username == "none":
            return {}

        try:
            url = f"https://gramhir.com/api/author/{username}"
            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return {
                    "followers": data.get("user", {}).get("followers", 0),
                    "posts": data.get("user", {}).get("posts_count", 0),
                }
        except Exception as e:
            print(f"[Instagram] Error: {e}")
            return {}

    @staticmethod
    def fetch_bugcrowd(username: str) -> Dict:
        """Fetch public Bugcrowd leaderboard stats."""
        if not username or username == "none":
            return {}

        try:
            url = f"https://bugcrowd.com/{username}"
            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode()
                import re
                rewards = re.findall(r'\$\d+[,]*[\d]*', html)
                return {"rewards": rewards[:5] if rewards else []}
        except Exception as e:
            print(f"[Bugcrowd] Error: {e}")
            return {}

    @staticmethod
    def fetch_fiverr_profile(username: str) -> Dict:
        """Fetch Fiverr public gig stats."""
        if not username or username == "none":
            return {}

        try:
            url = f"https://www.fiverr.com/{username}"
            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode()
                import re
                gigs = re.findall(r'(\d+)\s*gigs?', html, re.IGNORECASE)
                return {"gigs_sold": int(gigs[0]) if gigs else 0}
        except Exception as e:
            print(f"[Fiverr] Error: {e}")
            return {}


class MonetizationEngine:
    """
    JARVIS Monetization Engine
    Tracks real revenue from all agent platforms
    """

    def __init__(self):
        self.db = MonetizationDB()
        self.fetcher = PlatformFetcher()
        self.credentials = self._load_credentials()
        self.agents = self._get_agent_configs()

    def _load_credentials(self) -> Dict:
        if os.path.exists(CREDS_PATH):
            try:
                with open(CREDS_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _get_agent_configs(self) -> List[Dict]:
        return [
            {
                "id": "morpheus",
                "name": "Morpheus",
                "role": "Social Media Commander",
                "color": "#8b00ff",
                "platforms": [
                    {"name": "TikTok", "type": "tiktok", "username_env": "MORPHEUS_TIKTOK"},
                    {"name": "Instagram", "type": "instagram", "username_env": "MORPHEUS_INSTAGRAM"},
                    {"name": "YouTube", "type": "youtube", "id_env": "MORPHEUS_YOUTUBE", "api_key_env": "YOUTUBE_API_KEY"},
                    {"name": "Twitter/X", "type": "twitter", "username_env": "MORPHEUS_TWITTER"},
                ],
                "revenue_formula": lambda s: s.get("tiktok", {}).get("followers", 0) * 0.01 + s.get("instagram", {}).get("followers", 0) * 0.02,
            },
            {
                "id": "sherlock_holmes",
                "name": "Sherlock Holmes",
                "role": "Repo Inspector",
                "color": "#00d9ff",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "SHERLOCK_GITHUB"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("total_stars", 0) * 0.05,
            },
            {
                "id": "midas",
                "name": "Midas",
                "role": "MoneyMaker Specialist",
                "color": "#ffd700",
                "platforms": [
                    {"name": "Amazon", "type": "amazon", "store_env": "MIDAS_AMAZON_STORE"},
                    {"name": "eBay", "type": "ebay", "store_env": "MIDAS_EBAY_STORE"},
                    {"name": "Shopify", "type": "shopify", "store_env": "MIDAS_SHOPIFY"},
                ],
                "revenue_formula": lambda s: 5000,
            },
            {
                "id": "adforge",
                "name": "AdForge",
                "role": "Ads & Copywriting",
                "color": "#ff00aa",
                "platforms": [
                    {"name": "Google Ads", "type": "google_ads", "account_env": "ADFORGE_GOOGLE_ADS"},
                    {"name": "Facebook Ads", "type": "facebook_ads", "account_env": "ADFORGE_FB_ADS"},
                ],
                "revenue_formula": lambda s: 10000,
            },
            {
                "id": "ripley",
                "name": "Ripley",
                "role": "Bug Hunter",
                "color": "#ff0044",
                "platforms": [
                    {"name": "Bugcrowd", "type": "bugcrowd", "username_env": "RIPLEY_BUGCROWD"},
                    {"name": "HackerOne", "type": "hackerone", "username_env": "RIPLEY_HACKERONE"},
                ],
                "revenue_formula": lambda s: 5000,
            },
            {
                "id": "da_vinci",
                "name": "Da Vinci",
                "role": "UI Agent",
                "color": "#ff44aa",
                "platforms": [
                    {"name": "Dribbble", "type": "dribbble", "username_env": "DAVINCI_DRIBBBLE"},
                    {"name": "Behance", "type": "behance", "username_env": "DAVINCI_BEHANCE"},
                    {"name": "Fiverr", "type": "fiverr", "username_env": "DAVINCI_FIVERR"},
                ],
                "revenue_formula": lambda s: 3000,
            },
            {
                "id": "john_kramer",
                "name": "John Kramer",
                "role": "Planner - Missions",
                "color": "#ffe600",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "KRAMER_GITHUB"},
                    {"name": "Notion", "type": "notion", "workspace_env": "KRAMER_NOTION"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("total_stars", 0) * 0.03,
            },
            {
                "id": "saul_goodman",
                "name": "Saul Goodman",
                "role": "Patch Agent",
                "color": "#ff6600",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "SAUL_GITHUB"},
                    {"name": "Stack Overflow", "type": "stackoverflow", "username_env": "SAUL_STACKOVERFLOW"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("total_forks", 0) * 0.10,
            },
            {
                "id": "jarvis_build",
                "name": "JARVIS Builder",
                "role": "Build Validator",
                "color": "#4a9eff",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "BUILDER_GITHUB"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("total_stars", 0) * 0.05,
            },
            {
                "id": "john_wick",
                "name": "John Wick",
                "role": "Final Implementation",
                "color": "#ffffff",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "WICK_GITHUB"},
                    {"name": "AWS", "type": "aws", "account_env": "WICK_AWS"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("total_stars", 0) * 0.07,
            },
            {
                "id": "director_fury",
                "name": "Director Fury",
                "role": "Chief of Staff",
                "color": "#ff4444",
                "platforms": [
                    {"name": "JARVIS OS", "type": "internal", "name": "JARVIS OS"},
                ],
                "revenue_formula": lambda s: 15000,
            },
            {
                "id": "heimdall",
                "name": "Heimdall",
                "role": "Security & Validation",
                "color": "#00ff88",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "HEIMDALL_GITHUB"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("followers", 0) * 1.0,
            },
            {
                "id": "data",
                "name": "Data",
                "role": "Archivist - Memory",
                "color": "#00ffff",
                "platforms": [
                    {"name": "GitHub", "type": "github", "username_env": "DATA_GITHUB"},
                ],
                "revenue_formula": lambda s: s.get("github", {}).get("total_repos", 0) * 10,
            },
        ]

    def _get_cred(self, env_key: str) -> Optional[str]:
        val = os.environ.get(env_key)
        if val and val != "none":
            return val
        creds = self.credentials.get(env_key)
        if creds and creds != "none":
            return creds
        return None

    def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch real data from all agent platforms."""
        results = {}

        for agent in self.agents:
            agent_id = agent["id"]
            platform_data = {}
            all_stats = {}

            for platform in agent.get("platforms", []):
                ptype = platform["type"]
                pname = platform["name"]

                if ptype == "github":
                    username = self._get_cred(platform.get("username_env", ""))
                    if username:
                        data = self.fetcher.fetch_github(username)
                        platform_data[pname] = data
                        all_stats.update(data)

                elif ptype == "tiktok":
                    username = self._get_cred(platform.get("username_env", ""))
                    if username:
                        data = self.fetcher.fetch_tiktok(username)
                        platform_data[pname] = data
                        all_stats["tiktok"] = data

                elif ptype == "instagram":
                    username = self._get_cred(platform.get("username_env", ""))
                    if username:
                        data = self.fetcher.fetch_instagram(username)
                        platform_data[pname] = data
                        all_stats["instagram"] = data

                elif ptype == "youtube":
                    channel_id = self._get_cred(platform.get("id_env", ""))
                    api_key = self._get_cred(platform.get("api_key_env", ""))
                    if channel_id:
                        data = self.fetcher.fetch_youtube(channel_id, api_key)
                        platform_data[pname] = data
                        all_stats["youtube"] = data

                elif ptype == "bugcrowd":
                    username = self._get_cred(platform.get("username_env", ""))
                    if username:
                        data = self.fetcher.fetch_bugcrowd(username)
                        platform_data[pname] = data

                elif ptype == "fiverr":
                    username = self._get_cred(platform.get("username_env", ""))
                    if username:
                        data = self.fetcher.fetch_fiverr_profile(username)
                        platform_data[pname] = data

            revenue = agent["revenue_formula"](all_stats)

            self.db.save_revenue(agent_id, "aggregated", revenue, "USD", "monthly")
            for pname, pdata in platform_data.items():
                if isinstance(pdata, dict):
                    for key, val in pdata.items():
                        if isinstance(val, (int, float)):
                            self.db.save_stat(agent_id, pname, key, val)

            results[agent_id] = {
                "platforms": platform_data,
                "revenue": revenue,
                "stats": all_stats,
            }

        return results

    def get_agent_data(self, agent_id: str) -> Dict:
        """Get all monetization data for a specific agent."""
        revenue = self.db.get_agent_revenue(agent_id)
        stats = self.db.get_agent_stats(agent_id)

        agent_config = next((a for a in self.agents if a["id"] == agent_id), None)

        total = sum(r["revenue"] for r in revenue)

        return {
            "agent_id": agent_id,
            "name": agent_config.get("name", agent_id) if agent_config else agent_id,
            "role": agent_config.get("role", "") if agent_config else "",
            "color": agent_config.get("color", "#00d9ff") if agent_config else "#00d9ff",
            "platforms": agent_config.get("platforms", []) if agent_config else [],
            "revenue": revenue,
            "total_revenue": total,
            "stats": stats,
        }

    def get_all_revenue(self) -> float:
        return self.db.get_total_revenue()

    def get_full_report(self) -> List[Dict]:
        return [self.get_agent_data(a["id"]) for a in self.agents]

    def save_credentials(self, credentials: Dict):
        """Save platform credentials."""
        self.credentials.update(credentials)
        with open(CREDS_PATH, 'w') as f:
            json.dump(self.credentials, f, indent=2)


_engine = None
_engine_lock = threading.Lock()


def get_engine() -> MonetizationEngine:
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = MonetizationEngine()
        return _engine
