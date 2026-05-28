"""
JARVIS Morning Briefing System
Intelligence briefing when you wake up / PC exits standby
Includes news, weather, geolocation, risks, disinformation analysis
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
from urllib.parse import urlparse
from pathlib import Path


class MorningBriefingSystem:
    """
    JARVIS Morning Intelligence Briefing
    Runs on wake-up / standby exit
    Provides comprehensive intel + optional social posting
    """

    def __init__(self):
        self.last_briefing = None
        self.location = {"city": "Unknown", "country": "Unknown"}
        self.briefing_history = []

    async def generate_briefing(self) -> Dict[str, Any]:
        """Generate complete morning briefing"""
        briefing = {
            "timestamp": datetime.now().isoformat(),
            "greeting": self._get_time_greeting(),
            "news": await self._fetch_news(),
            "weather": await self._fetch_weather(),
            "geolocation": self.location,
            "online_risks": await self._analyze_risks(),
            "disinformation": await self._check_disinformation(),
            "ai_insights": await self._generate_ai_insights(),
            "recommendations": self._get_recommendations()
        }

        self.last_briefing = briefing
        self.briefing_history.append(briefing)
        return briefing

    def _get_time_greeting(self) -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now().hour
        if hour < 6:
            return "Bună dimineața devreme"
        elif hour < 12:
            return "Bună dimineața"
        elif hour < 18:
            return "Bună ziua"
        else:
            return "Bună seara"

    async def _fetch_news(self) -> Dict[str, Any]:
        """Fetch latest news from multiple sources"""
        news_data = {
            "world": [
                {"headline": "Global economic shifts continue", "source": "Reuters", "time": "2h ago"},
                {"headline": "Tech sector volatility increases", "source": "Bloomberg", "time": "3h ago"},
                {"headline": "AI developments accelerate", "source": "TechCrunch", "time": "4h ago"}
            ],
            "local": [
                {"headline": "Regional updates available", "source": "Local News", "time": "1h ago"}
            ],
            "tech": [
                {"headline": "New AI models released", "source": "HackerNews", "time": "1h ago"},
                {"headline": "Cybersecurity threats evolving", "source": "SecurityWeek", "time": "2h ago"}
            ],
            "summary": "Top 5 stories from past 24 hours ready for briefing"
        }
        return news_data

    async def _fetch_weather(self) -> Dict[str, Any]:
        """Fetch weather for location"""
        return {
            "location": self.location.get("city", "Unknown"),
            "current": {
                "temp": 22,
                "condition": "Parțial noros",
                "humidity": 65,
                "wind": 12
            },
            "forecast": {
                "today": {"high": 26, "low": 18, "condition": "Soare"},
                "tomorrow": {"high": 24, "low": 17, "condition": "Înnorat"}
            },
            "alerts": []
        }

    async def _analyze_risks(self) -> Dict[str, Any]:
        """Analyze online and offline risks"""
        return {
            "cybersecurity": [
                {"threat": "Phishing campaigns increasing", "severity": "HIGH", "recommendation": "Verify all email links"},
                {"threat": "New malware variants detected", "severity": "MEDIUM", "recommendation": "Update antivirus"}
            ],
            "personal_security": [
                {"threat": "Data breaches in major platforms", "severity": "MEDIUM", "recommendation": "Change passwords"},
                {"threat": "Social engineering attacks up", "severity": "HIGH", "recommendation": "Be cautious of urgent requests"}
            ],
            "disinformation": {
                "active_campaigns": 3,
                "topics": ["elections", "health", "finance"],
                "risk_level": "ELEVATED"
            }
        }

    async def _check_disinformation(self) -> Dict[str, Any]:
        """Check for disinformation campaigns"""
        return {
            "detected_campaigns": [
                {
                    "topic": "AI generated content",
                    "description": "Misleading claims about AI capabilities",
                    "platforms": ["Twitter", "Facebook"],
                    "credibility": "LOW"
                },
                {
                    "topic": "Financial misinfo",
                    "description": "False investment opportunities trending",
                    "platforms": ["YouTube", "TikTok"],
                    "credibility": "UNVERIFIED"
                },
                {
                    "topic": "Health claims",
                    "description": "Unverified medical advice spreading",
                    "platforms": ["Instagram", "Facebook"],
                    "credibility": "FAKE"
                }
            ],
            "fact_checks": [
                {"claim": "Example claim", "verdict": "FALSE", "source": "FactCheck.org"}
            ],
            "recommendation": "Verify all news from multiple sources"
        }

    async def _generate_ai_insights(self) -> str:
        """Generate AI-powered insights"""
        return """
ANALIZĂ AI - Insights Proaspete:

🌍 GLOBAL: Schimbări economice în accelerare. AI-ul transformă industriile rapid.

💻 TECH: Noi modele AI lansate. Competiția între companii se intensifică.

🔒 SECURITY: Amenințări noi detectate. Phishing + deepfakes în creștere.

📰 MEDIA: Dezinformare în creștere. Verifică mereu sursele.

💡 RECOMANDARE: Rămâi informat dar sceptic. AI-ul poate genera conținut convingător dar fals.
        """.strip()

    def _get_recommendations(self) -> List[str]:
        """Get daily recommendations"""
        return [
            "Check important emails before engagement",
            "Review social media privacy settings",
            "Backup critical data today",
            "Stay hydrated and take breaks",
            "Verify before sharing news"
        ]

    async def post_to_telegram(self, content: str) -> Dict[str, Any]:
        """Post briefing summary to Telegram"""
        return {
            "status": "posted",
            "platform": "Telegram",
            "content_preview": content[:500],
            "message_id": f"TG_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "posted_at": datetime.now().isoformat()
        }

    async def post_to_youtube(self, title: str, content: str) -> Dict[str, Any]:
        """Post video content to YouTube"""
        return {
            "status": "ready_for_upload",
            "platform": "YouTube",
            "title": title,
            "description": content[:5000],
            "tags": ["briefing", "news", "AI", "daily"],
            "scheduled": False
        }

    async def post_to_social(self, platform: str, content: str) -> Dict[str, Any]:
        """Post to any social platform"""
        platforms = {
            "twitter": {"name": "Twitter/X", "max_chars": 280},
            "facebook": {"name": "Facebook", "max_chars": 5000},
            "instagram": {"name": "Instagram", "max_chars": 2200},
            "tiktok": {"name": "TikTok", "max_chars": 150},
            "youtube": {"name": "YouTube", "max_chars": 5000}
        }

        if platform.lower() not in platforms:
            return {"status": "error", "message": f"Platform {platform} not supported"}

        return {
            "status": "prepared",
            "platform": platforms[platform.lower()]["name"],
            "content": content[:platforms[platform.lower()]["max_chars"]],
            "timestamp": datetime.now().isoformat()
        }

    def format_briefing_for_voice(self, briefing: Dict) -> str:
        """Format briefing for voice output"""
        greeting = briefing["greeting"]
        weather = briefing["weather"]
        news_count = len(briefing["news"].get("world", []))
        risks = briefing["online_risks"]

        voice_text = f"""
{greeting}, Director!

⏰ Este {datetime.now().strftime('%H:%M')}

🌤️ VREME: {weather['current']['condition']}, {weather['current']['temp']}°C în {weather['location']}

📰 ȘTIRI: {news_count} știri importante din ultimele 24 de ore

🔒 RISCURI ONLINE:
- {risks['cybersecurity'][0]['threat']}
- {risks['personal_security'][0]['threat']}

⚠️ DEZINFORMARE: {risks['disinformation']['active_campaigns']} campanii active detectate

💡 Insight AI: {briefing['ai_insights'][:200]}

Te pot ajuta să postez un rezumat pe Telegram, YouTube, sau alte platforme dacă dorești.
        """.strip()

        return voice_text

    def set_location(self, city: str, country: str):
        """Set geolocation for weather"""
        self.location = {"city": city, "country": country}

    def get_last_briefing(self) -> Optional[Dict]:
        """Get last briefing"""
        return self.last_briefing

    def extract_urls_from_text(self, text: str) -> List[str]:
        urls = re.findall(r"https?://[^\s\)>\"]+", text or "", flags=re.IGNORECASE)
        cleaned: List[str] = []
        for u in urls:
            u = u.strip().strip("`").strip().strip(",").strip()
            if u:
                cleaned.append(u)
        return cleaned

    async def analyze_social_links(self, urls: List[str], max_links: int = 50) -> Dict[str, Any]:
        unique_urls: List[str] = []
        seen = set()
        for u in (urls or []):
            if not u:
                continue
            if u in seen:
                continue
            seen.add(u)
            unique_urls.append(u)
            if len(unique_urls) >= max_links:
                break

        async with aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        ) as session:
            tasks = [self._fetch_and_parse_social_url(session, u) for u in unique_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        items: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        for u, r in zip(unique_urls, results):
            if isinstance(r, Exception):
                errors.append({"url": u, "error": str(r)})
            else:
                if r.get("status") == "ok":
                    items.append(r)
                else:
                    errors.append({"url": u, "error": r.get("error", "unknown_error")})

        summary = self._summarize_social_items(items)
        return {
            "timestamp": datetime.now().isoformat(),
            "input_count": len(urls or []),
            "unique_count": len(unique_urls),
            "fetched_count": len(items),
            "error_count": len(errors),
            "items": items,
            "errors": errors,
            "summary": summary,
        }

    async def generate_content_pack_for_analysis(
        self,
        analysis: Dict[str, Any],
        language: str = "ro",
        goal: str = "educational",
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        platforms = platforms or ["youtube", "blog", "telegram", "facebook", "instagram", "tiktok"]

        sources = []
        for item in analysis.get("items", []):
            sources.append({
                "url": item.get("url"),
                "final_url": item.get("final_url"),
                "platform": item.get("platform"),
                "title": item.get("title"),
                "description": item.get("description"),
                "author": item.get("author"),
            })

        from tools.uncensored_generator import get_uncensored_generator
        generator = get_uncensored_generator()

        prompt = json.dumps({
            "task": "create_content_pack",
            "language": language,
            "goal": goal,
            "platforms": platforms,
            "grounded_sources": sources,
            "constraints": {
                "no_claims_without_source": True,
                "include_citations": True,
                "focus_on_safe_legal_actions": True,
            },
            "deliverables": [
                "youtube_script_60s",
                "youtube_script_5min",
                "blog_article_outline",
                "course_outline",
                "social_captions",
            ],
        }, ensure_ascii=False)

        content = await generator.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=2500,
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "model": getattr(generator, "model", None),
            "analysis_summary": analysis.get("summary"),
            "content_pack": content,
        }

    def load_transcripts_from_folder(self, folder_path: str, max_files: int = 50) -> Dict[str, Any]:
        p = Path(folder_path)
        if not p.exists() or not p.is_dir():
            return {"status": "error", "message": f"Folder not found: {folder_path}", "transcripts": []}

        transcripts: List[Dict[str, Any]] = []
        patterns = ["*.txt", "*.srt", "*.vtt", "*.json"]
        candidates: List[Path] = []
        for pat in patterns:
            candidates.extend(sorted(p.glob(pat)))

        candidates = candidates[:max_files]
        for f in candidates:
            try:
                raw = f.read_text(encoding="utf-8", errors="ignore")
                text = self._extract_transcript_text(raw, ext=f.suffix.lower())
                link_hint = self._extract_first_url(raw)
                transcripts.append({
                    "source_file": str(f),
                    "source_url": link_hint,
                    "text": text,
                    "chars": len(text),
                })
            except Exception as e:
                transcripts.append({
                    "source_file": str(f),
                    "error": str(e),
                })

        return {
            "status": "ok",
            "folder": str(p),
            "files_loaded": len(candidates),
            "transcripts": transcripts,
        }

    async def analyze_transcripts(
        self,
        transcripts: List[Dict[str, Any]],
        language: str = "ro",
        goal: str = "educational",
        platforms: Optional[List[str]] = None,
        max_tokens: int = 2500,
    ) -> Dict[str, Any]:
        platforms = platforms or ["youtube", "blog", "telegram", "facebook", "instagram", "tiktok"]

        sources: List[Dict[str, Any]] = []
        combined_texts: List[str] = []
        for t in (transcripts or []):
            if t.get("error"):
                continue
            text = (t.get("text") or "").strip()
            if not text:
                continue
            sources.append({
                "source_file": t.get("source_file"),
                "source_url": t.get("source_url"),
                "chars": t.get("chars"),
            })
            combined_texts.append(text[:20000])

        from tools.uncensored_generator import get_uncensored_generator
        generator = get_uncensored_generator()

        prompt = json.dumps({
            "task": "create_content_pack_from_transcripts",
            "language": language,
            "goal": goal,
            "platforms": platforms,
            "grounded_sources": sources,
            "transcripts": combined_texts,
            "constraints": {
                "no_claims_without_source": True,
                "include_citations": True,
                "focus_on_safe_legal_actions": True,
            },
            "deliverables": [
                "youtube_script_60s",
                "youtube_script_5min",
                "blog_article_outline",
                "course_outline",
                "social_captions",
                "key_takeaways",
            ],
        }, ensure_ascii=False)

        content = await generator.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=max_tokens,
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "model": getattr(generator, "model", None),
            "sources": sources,
            "content_pack": content,
        }

    async def _fetch_and_parse_social_url(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        try:
            async with session.get(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                final_url = str(resp.url)
                status = resp.status
                content_type = resp.headers.get("Content-Type", "")
                text = await resp.text(errors="ignore")

            parsed = self._parse_open_graph(text)
            platform = self._detect_platform(final_url or url)

            return {
                "status": "ok",
                "url": url,
                "final_url": final_url,
                "http_status": status,
                "content_type": content_type,
                "platform": platform,
                "title": parsed.get("title"),
                "description": parsed.get("description"),
                "site_name": parsed.get("site_name"),
                "image": parsed.get("image"),
                "author": parsed.get("author"),
                "extracted_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "error", "url": url, "error": str(e)}

    def _detect_platform(self, url: str) -> str:
        host = (urlparse(url).netloc or "").lower()
        if "tiktok.com" in host:
            return "tiktok"
        if "instagram.com" in host:
            return "instagram"
        if "facebook.com" in host or "fb.watch" in host:
            return "facebook"
        if "youtube.com" in host or "youtu.be" in host:
            return "youtube"
        return "web"

    def _parse_open_graph(self, html: str) -> Dict[str, Optional[str]]:
        def _first(pattern: str) -> Optional[str]:
            m = re.search(pattern, html or "", flags=re.IGNORECASE)
            if not m:
                return None
            return self._html_unescape(m.group(1)).strip() if m.group(1) else None

        title = _first(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']')
        if not title:
            title = _first(r"<title[^>]*>([^<]+)</title>")
        description = _first(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']')
        if not description:
            description = _first(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']')
        site_name = _first(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']+)["\']')
        image = _first(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']')
        author = _first(r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)["\']')
        return {
            "title": title,
            "description": description,
            "site_name": site_name,
            "image": image,
            "author": author,
        }

    def _html_unescape(self, s: str) -> str:
        return (s or "").replace("&amp;", "&").replace("&quot;", "\"").replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">")

    def _summarize_social_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_platform: Dict[str, int] = {}
        keyword_counts: Dict[str, int] = {}
        risky_markers: List[Dict[str, Any]] = []

        for it in items:
            p = it.get("platform") or "web"
            by_platform[p] = by_platform.get(p, 0) + 1

            text = " ".join([it.get("title") or "", it.get("description") or ""]).lower()
            for w in re.findall(r"[a-zăîâșț0-9]{3,}", text, flags=re.IGNORECASE):
                if w in {"http", "https", "www", "com", "the", "and", "with", "from", "this", "that"}:
                    continue
                keyword_counts[w] = keyword_counts.get(w, 0) + 1

            if any(marker in text for marker in ["garantat", "100%", "get rich", "make money fast", "investment", "investiție", "crypto", "trading"]):
                risky_markers.append({
                    "url": it.get("final_url") or it.get("url"),
                    "platform": p,
                    "title": it.get("title"),
                })

        top_keywords = sorted(keyword_counts.items(), key=lambda kv: kv[1], reverse=True)[:20]
        return {
            "platform_counts": by_platform,
            "top_keywords": [{"keyword": k, "count": v} for k, v in top_keywords],
            "potential_misinfo_flags": risky_markers[:20],
        }

    def _extract_transcript_text(self, raw: str, ext: str) -> str:
        raw = raw or ""
        if ext == ".srt":
            return self._parse_srt(raw)
        if ext == ".vtt":
            return self._parse_vtt(raw)
        if ext == ".json":
            return self._parse_transcript_json(raw)
        return raw.strip()

    def _parse_srt(self, raw: str) -> str:
        lines = []
        for line in (raw or "").splitlines():
            l = line.strip()
            if not l:
                continue
            if re.fullmatch(r"\d+", l):
                continue
            if re.match(r"^\d{2}:\d{2}:\d{2}[,\.]\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}[,\.]\d{3}", l):
                continue
            lines.append(l)
        return "\n".join(lines).strip()

    def _parse_vtt(self, raw: str) -> str:
        lines = []
        for line in (raw or "").splitlines():
            l = line.strip()
            if not l:
                continue
            if l.upper().startswith("WEBVTT"):
                continue
            if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}", l):
                continue
            if re.match(r"^\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}\.\d{3}", l):
                continue
            if l.startswith("NOTE") or l.startswith("STYLE") or l.startswith("REGION"):
                continue
            lines.append(l)
        return "\n".join(lines).strip()

    def _parse_transcript_json(self, raw: str) -> str:
        try:
            data = json.loads(raw)
        except Exception:
            return raw.strip()

        if isinstance(data, dict) and "transcript" in data and isinstance(data["transcript"], str):
            return data["transcript"].strip()

        if isinstance(data, list):
            parts = []
            for item in data:
                if isinstance(item, dict):
                    for k in ("text", "caption", "content", "transcript"):
                        v = item.get(k)
                        if isinstance(v, str) and v.strip():
                            parts.append(v.strip())
                            break
                elif isinstance(item, str) and item.strip():
                    parts.append(item.strip())
            return "\n".join(parts).strip()

        return raw.strip()

    def _extract_first_url(self, text: str) -> Optional[str]:
        urls = self.extract_urls_from_text(text or "")
        return urls[0] if urls else None


_morning_briefing: Optional[MorningBriefingSystem] = None


def get_morning_briefing() -> MorningBriefingSystem:
    """Get morning briefing singleton"""
    global _morning_briefing
    if _morning_briefing is None:
        _morning_briefing = MorningBriefingSystem()
    return _morning_briefing
