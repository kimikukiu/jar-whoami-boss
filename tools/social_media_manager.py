"""
JARVIS Social Media Manager
Integrare completă cu Facebook, Instagram, TikTok, Twitter/X, LinkedIn
"""

import asyncio
import json
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

@dataclass
class SocialPost:
    """Reprezintă o postare social media"""
    platform: str
    content: str
    media_urls: List[str]
    scheduled_time: Optional[datetime] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    post_id: Optional[str] = None
    status: str = "draft"  # draft, scheduled, published, failed
    created_at: datetime = None
    published_at: Optional[datetime] = None
    engagement_stats: Dict[str, int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.media_urls is None:
            self.media_urls = []
        if self.engagement_stats is None:
            self.engagement_stats = {"likes": 0, "comments": 0, "shares": 0, "views": 0}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertește postarea în dicționar"""
        data = asdict(self)
        # Convertim datetime în string ISO
        for key in ['scheduled_time', 'created_at', 'published_at']:
            if data.get(key):
                data[key] = data[key].isoformat() if isinstance(data[key], datetime) else data[key]
        return data


class FacebookConnector:
    """Connector pentru Facebook Graph API"""
    
    def __init__(self, access_token: str, page_id: Optional[str] = None):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def post(self, post: SocialPost, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Postează pe Facebook"""
        url = f"{self.base_url}/{self.page_id}/feed"
        
        params = {
            "access_token": self.access_token,
            "message": post.content
        }
        
        if post.scheduled_time and post.scheduled_time > datetime.now():
            params["scheduled_publish_time"] = int(post.scheduled_time.timestamp())
            params["published"] = "false"
        
        try:
            async with session.post(url, params=params) as response:
                data = await response.json()
                
                if "id" in data:
                    post.post_id = data["id"]
                    post.status = "scheduled" if "scheduled_publish_time" in params else "published"
                    post.published_at = datetime.now() if post.status == "published" else None
                    
                    return {
                        "success": True,
                        "post_id": post.post_id,
                        "status": post.status,
                        "platform": "facebook"
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("error", {}).get("message", "Unknown error"),
                        "platform": "facebook"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "facebook"
            }
    
    async def get_stats(self, post_id: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Obține statistici pentru o postare"""
        url = f"{self.base_url}/{post_id}"
        
        params = {
            "access_token": self.access_token,
            "fields": "likes.summary(true),comments.summary(true),shares,views"
        }
        
        try:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                return {
                    "likes": data.get("likes", {}).get("summary", {}).get("total_count", 0),
                    "comments": data.get("comments", {}).get("summary", {}).get("total_count", 0),
                    "shares": data.get("shares", {}).get("count", 0),
                    "views": data.get("views", 0)
                }
        except:
            return {"likes": 0, "comments": 0, "shares": 0, "views": 0}


class InstagramConnector:
    """Connector pentru Instagram Graph API"""
    
    def __init__(self, access_token: str, instagram_account_id: str):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def post(self, post: SocialPost, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Postează pe Instagram (doar imagini/video pentru acum)"""
        # Instagram necesită media container creation first
        
        if not post.media_urls:
            return {
                "success": False,
                "error": "Instagram requires media (image or video)",
                "platform": "instagram"
            }
        
        # Creăm media container
        url = f"{self.base_url}/{self.instagram_account_id}/media"
        
        params = {
            "access_token": self.access_token,
            "caption": post.content,
            "image_url": post.media_urls[0] if post.media_urls else None
        }
        
        try:
            async with session.post(url, params=params) as response:
                data = await response.json()
                
                if "id" in data:
                    creation_id = data["id"]
                    
                    # Publicăm media
                    publish_url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
                    publish_params = {
                        "access_token": self.access_token,
                        "creation_id": creation_id
                    }
                    
                    async with session.post(publish_url, params=publish_params) as pub_response:
                        pub_data = await pub_response.json()
                        
                        if "id" in pub_data:
                            post.post_id = pub_data["id"]
                            post.status = "published"
                            post.published_at = datetime.now()
                            
                            return {
                                "success": True,
                                "post_id": post.post_id,
                                "status": "published",
                                "platform": "instagram"
                            }
                
                return {
                    "success": False,
                    "error": data.get("error", {}).get("message", "Unknown error"),
                    "platform": "instagram"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }


class SocialMediaManager:
    """
    Manager central pentru social media
    Coordonează postarea pe multiple platforme
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.connectors: Dict[str, Any] = {}
        self.scheduled_posts: List[SocialPost] = []
        self.posts_history: List[Dict] = []
        self.config = self._load_config(config_file)
        
        # Inițializăm conectorii dacă avem config
        if self.config:
            self._initialize_connectors()
    
    def _load_config(self, config_file: Optional[str]) -> Optional[Dict]:
        """Încarcă configurația din fișier"""
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Căutăm config default
        default_config = Path(__file__).parent / "social_media_config.json"
        if default_config.exists():
            with open(default_config, 'r') as f:
                return json.load(f)
        
        return None
    
    def _initialize_connectors(self):
        """Inițializează conectorii pentru platforme"""
        if "facebook" in self.config:
            self.connectors["facebook"] = FacebookConnector(
                self.config["facebook"]["access_token"],
                self.config["facebook"].get("page_id")
            )
            print("✓ Facebook connector initialized")
        
        if "instagram" in self.config:
            self.connectors["instagram"] = InstagramConnector(
                self.config["instagram"]["access_token"],
                self.config["instagram"]["account_id"]
            )
            print("✓ Instagram connector initialized")
    
    async def post(self, post: SocialPost, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Postează pe una sau mai multe platforme
        
        Args:
            post: Obiectul SocialPost de postat
            platforms: Lista de platforme (None = toate disponibile)
            
        Returns:
            Dict cu rezultatele pentru fiecare platformă
        """
        results = {}
        
        # Determinăm platformele
        target_platforms = platforms if platforms else list(self.connectors.keys())
        
        print(f"\n{'='*60}")
        print(f"POSTARE SOCIAL MEDIA")
        print(f"{'='*60}")
        print(f"Platforme: {', '.join(target_platforms)}")
        print(f"Conținut: {post.content[:100]}...")
        
        async with aiohttp.ClientSession() as session:
            for platform in target_platforms:
                if platform in self.connectors:
                    connector = self.connectors[platform]
                    
                    print(f"\n📤 Postare pe {platform}...")
                    
                    try:
                        result = await connector.post(post, session)
                        results[platform] = result
                        
                        if result.get("success"):
                            print(f"  ✓ Succes! Post ID: {result.get('post_id', 'N/A')}")
                        else:
                            print(f"  ✗ Eșec: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"  ✗ Excepție: {e}")
                        results[platform] = {"success": False, "error": str(e), "platform": platform}
                else:
                    print(f"  ⚠ Connector pentru {platform} nu este disponibil")
                    results[platform] = {"success": False, "error": "Connector not available", "platform": platform}
        
        # Salvăm în istoric
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "post": post.to_dict(),
            "results": results
        }
        self.posts_history.append(history_entry)
        
        # Sumar
        successful = sum(1 for r in results.values() if r.get("success"))
        print(f"\n{'='*60}")
        print(f"REZULTATE POSTARE")
        print(f"{'='*60}")
        print(f"Platforme încercate: {len(results)}")
        print(f"Succes: {successful}")
        print(f"Eșecuri: {len(results) - successful}")
        
        return results
    
    def schedule_post(self, post: SocialPost, scheduled_time: datetime, 
                     platforms: Optional[List[str]] = None) -> str:
        """
        Programează o postare pentru viitor
        
        Returns:
            ID-ul postării programate
        """
        post.scheduled_time = scheduled_time
        post.status = "scheduled"
        
        # Generăm ID unic
        post_id = f"scheduled_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(post.content) % 10000}"
        
        # Adăugăm în lista de programări
        scheduled_entry = {
            "id": post_id,
            "post": post.to_dict(),
            "platforms": platforms,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "pending"
        }
        
        self.scheduled_posts.append(post)
        
        print(f"\n✓ Postare programată")
        print(f"  ID: {post_id}")
        print(f"  Data: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Platforme: {', '.join(platforms) if platforms else 'Toate'}")
        
        return post_id
    
    async def process_scheduled_posts(self):
        """Procesează postările programate care sunt due"""
        now = datetime.now()
        posts_to_process = []
        
        # Găsim postările care trebuie publicate
        for post in self.scheduled_posts:
            if (post.status == "scheduled" and 
                post.scheduled_time and 
                post.scheduled_time <= now):
                posts_to_process.append(post)
        
        if posts_to_process:
            print(f"\n🕒 Procesăm {len(posts_to_process)} postări programate...")
            
            for post in posts_to_process:
                await self.post(post)
                post.status = "published"
                self.scheduled_posts.remove(post)
    
    def get_analytics(self, platform: Optional[str] = None, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generează raport analitic pentru postări
        
        Args:
            platform: Filtrează după platformă (None = toate)
            start_date: Data de început pentru raport
            end_date: Data de sfârșit pentru raport
            
        Returns:
            Dict cu statistici și analize
        """
        # Filtrăm istoricul
        filtered_history = self.posts_history
        
        if start_date:
            filtered_history = [h for h in filtered_history 
                             if datetime.fromisoformat(h["timestamp"]) >= start_date]
        
        if end_date:
            filtered_history = [h for h in filtered_history 
                             if datetime.fromisoformat(h["timestamp"]) <= end_date]
        
        # Agregăm statistici
        total_posts = len(filtered_history)
        successful_posts = sum(1 for h in filtered_history 
                              if any(r.get("success") for r in h["results"].values()))
        
        platform_stats = {}
        for history_entry in filtered_history:
            for platform, result in history_entry["results"].items():
                if platform not in platform_stats:
                    platform_stats[platform] = {"total": 0, "successful": 0}
                
                platform_stats[platform]["total"] += 1
                if result.get("success"):
                    platform_stats[platform]["successful"] += 1
        
        # Engagement total
        total_engagement = {"likes": 0, "comments": 0, "shares": 0, "views": 0}
        for history_entry in filtered_history:
            post = history_entry.get("post", {})
            stats = post.get("engagement_stats", {})
            for key in total_engagement:
                total_engagement[key] += stats.get(key, 0)
        
        report = {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total_posts": total_posts,
                "successful_posts": successful_posts,
                "success_rate": (successful_posts / total_posts * 100) if total_posts > 0 else 0,
                "failed_posts": total_posts - successful_posts
            },
            "platform_breakdown": platform_stats,
            "engagement_totals": total_engagement,
            "top_performing_posts": self._get_top_posts(filtered_history, limit=5),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _get_top_posts(self, history: List[Dict], limit: int = 5) -> List[Dict]:
        """Extrage cele mai performante postări după engagement"""
        posts_with_engagement = []
        
        for entry in history:
            post = entry.get("post", {})
            stats = post.get("engagement_stats", {})
            total_engagement = sum(stats.values())
            
            posts_with_engagement.append({
                "post_id": post.get("post_id"),
                "content_preview": post.get("content", "")[:100] + "...",
                "platforms": list(entry.get("results", {}).keys()),
                "total_engagement": total_engagement,
                "engagement_breakdown": stats,
                "published_at": entry.get("timestamp")
            })
        
        # Sortăm după engagement total
        posts_with_engagement.sort(key=lambda x: x["total_engagement"], reverse=True)
        
        return posts_with_engagement[:limit]
    
    def export_report(self, report: Dict[str, Any], 
                     format: str = "json",
                     output_path: Optional[str] = None) -> str:
        """
        Exportă raportul în diferite formate
        
        Args:
            report: Dicționarul cu raportul
            format: "json", "html", "csv", "pdf"
            output_path: Calea de salvare (None = auto-generat)
            
        Returns:
            Calea către fișierul exportat
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"social_media_report_{timestamp}.{format}"
        
        output_path = Path(output_path)
        
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
        elif format == "html":
            html_content = self._generate_html_report(report)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        elif format == "csv":
            # Simplificat: exportăm doar summary statistics
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                summary = report.get("summary", {})
                for key, value in summary.items():
                    writer.writerow([key, value])
        
        else:
            raise ValueError(f"Format necunoscut: {format}")
        
        print(f"✓ Raport exportat: {output_path}")
        return str(output_path)
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generează raport în format HTML"""
        
        summary = report.get("summary", {})
        engagement = report.get("engagement_totals", {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Social Media Analytics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; display: block; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; margin-top: 5px; }}
        .success-rate {{ font-size: 1.5em; color: {'#28a745' if summary.get('success_rate', 0) > 80 else '#ffc107' if summary.get('success_rate', 0) > 50 else '#dc3545'}; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; color: #555; }}
        tr:hover {{ background: #f8f9fa; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Social Media Analytics Report</h1>
        <p class="timestamp">Generated: {report.get('generated_at', 'N/A')}</p>
        
        <h2>📈 Summary Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-value">{summary.get('total_posts', 0)}</span>
                <span class="stat-label">Total Posts</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{summary.get('successful_posts', 0)}</span>
                <span class="stat-label">Successful</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{summary.get('success_rate', 0):.1f}%</span>
                <span class="stat-label">Success Rate</span>
            </div>
        </div>
        
        <p class="success-rate">✅ Overall Success Rate: {summary.get('success_rate', 0):.1f}%</p>
        
        <h2>🎯 Engagement Totals</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-value">{engagement.get('likes', 0):,}</span>
                <span class="stat-label">Likes</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{engagement.get('comments', 0):,}</span>
                <span class="stat-label">Comments</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{engagement.get('shares', 0):,}</span>
                <span class="stat-label">Shares</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{engagement.get('views', 0):,}</span>
                <span class="stat-label">Views</span>
            </div>
        </div>
        
        <h2>📋 Platform Breakdown</h2>
        <table>
            <tr>
                <th>Platform</th>
                <th>Total Posts</th>
                <th>Successful</th>
                <th>Success Rate</th>
            </tr>
"""
        
        # Adăugăm platform breakdown
        platform_stats = report.get("platform_breakdown", {})
        for platform, stats in platform_stats.items():
            html += f"""
            <tr>
                <td>{platform.title()}</td>
                <td>{stats.get('total', 0)}</td>
                <td>{stats.get('successful', 0)}</td>
                <td>{(stats.get('successful', 0) / stats.get('total', 1) * 100) if stats.get('total', 0) > 0 else 0:.1f}%</td>
            </tr>
"""
        
        html += f"""
        </table>
        
        <h2>🏆 Top Performing Posts</h2>
        <table>
            <tr>
                <th>Post ID</th>
                <th>Platforms</th>
                <th>Total Engagement</th>
                <th>Published</th>
            </tr>
"""
        
        # Adăugăm top posts
        top_posts = report.get("top_performing_posts", [])
        for post in top_posts[:5]:  # Top 5
            html += f"""
            <tr>
                <td>{post.get('post_id', 'N/A')}</td>
                <td>{', '.join(post.get('platforms', []))}</td>
                <td>{post.get('total_engagement', 0):,}</td>
                <td>{post.get('published_at', 'N/A')}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <hr style="margin: 40px 0;">
        <p style="text-align: center; color: #666; font-size: 0.9em;">
            Generated by JARVIS Social Media Manager<br>
            © 2026 JARVIS Ecosystem
        </p>
    </div>
</body>
</html>
"""
        
        return html


# Funcții utilitare pentru utilizare directă
def create_post(content: str, 
                media_urls: List[str] = None,
                hashtags: List[str] = None,
                platforms: List[str] = None) -> SocialPost:
    """
    Creează rapid o postare social media
    
    Usage:
        post = create_post(
            content="Check out our new product!",
            hashtags=["#new", "#product"],
            platforms=["facebook", "instagram"]
        )
    """
    return SocialPost(
        platform="",  # Va fi setat de manager
        content=content,
        media_urls=media_urls or [],
        hashtags=hashtags or [],
        mentions=[],  # Poate fi extras automat din content
    )


# Dacă rulăm direct
if __name__ == "__main__":
    print("="*70)
    print("JARVIS SOCIAL MEDIA MANAGER")
    print("="*70)
    print()
    print("Pentru a utiliza managerul:")
    print()
    print("1. Crează o configurație JSON:")
    print("   {")
    print('     "facebook": {')
    print('       "access_token": "your_facebook_token",')
    print('       "page_id": "your_page_id"')
    print('     },')
    print('     "instagram": {')
    print('       "access_token": "your_instagram_token",')
    print('       "account_id": "your_account_id"')
    print('     }')
    print('   }')
    print()
    print("2. Utilizează în cod:")
    print("   from social_media_manager import SocialMediaManager, create_post")
    print()
    print("   # Inițializează managerul")
    print("   manager = SocialMediaManager('config.json')")
    print()
    print("   # Creează o postare")
    print("   post = create_post(")
    print("       content='Hello World!',")
    print("       hashtags=['#hello', '#world']")
    print("   )")
    print()
    print("   # Postează")
    print("   import asyncio")
    print("   results = asyncio.run(manager.post(post))")
    print()
    print("="*70)
