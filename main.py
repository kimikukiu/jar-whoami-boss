"""
JARVIS ECOSYSTEM - ORCHESTRA
Main entry point for the JARVIS AI system
Boot, control, and management of all 11 agents
Voice control and PC admin integration
"""
import sys
import os
sys.stdout.reconfigure(line_buffering=True)

import asyncio
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import MessageBus, TaskManager, Config
from agents.d_agents import DirectorFury
from agents.tier1 import Heimdall
from agents.tier2 import JohnKramer, Morpheus, SherlockHolmes, Data, Midas, AdForge
from agents.tier3 import SaulGoodman, JarvisBuild, Ripley, DaVinci, JohnWick

from aiohttp import web
import json


class JARVISOrchestra:
    """
    JARVIS Orchestra - Main System Controller
    Boots and manages all 11 agents in the ecosystem
    Includes voice control and PC admin capabilities
    """

    def __init__(self):
        self.config = Config()
        self.message_bus = MessageBus()
        self.task_manager = TaskManager(self.message_bus)
        self.agents: Dict[str, Any] = {}
        self._running = False
        self._boot_complete = False
        self._voice_enabled = False
        self._admin_control = None
        self._voice_system = None

    async def boot(self):
        """Boot all JARVIS agents"""
        print("""
        ╔══════════════════════════════════════════════════════════════╗
        ║                                                              ║
        ║     ██╗  ██╗███████╗███╗   ██╗ ██████╗                      ║
        ║     ██║ ██╔╝██╔════╝████╗  ██║██╔═══██╗                     ║
        ║     █████╔╝ █████╗  ██╔██╗ ██║██║   ██║                     ║
        ║     ██╔═██╗ ██╔══╝  ██║╚██╗██║██║   ██║                     ║
        ║     ██║  ██╗███████╗██║ ╚████║╚██████╔╝                     ║
        ║     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝  ECOSYSTEM           ║
        ║                                                              ║
        ║     Autonomous Agent Network - Ready for Commands            ║
        ╚══════════════════════════════════════════════════════════════╝
        """)

        print("[JARVIS] Initializing ecosystem...")
        print("[JARVIS] Loading configuration...")

        self.agents = {
            "director_fury": DirectorFury(self.message_bus, self.task_manager),
            "heimdall": Heimdall(self.message_bus),
            "john_kramer": JohnKramer(self.message_bus, self.task_manager),
            "morpheus": Morpheus(self.message_bus, self.task_manager),
            "sherlock_holmes": SherlockHolmes(self.message_bus),
            "data": Data(self.message_bus, self.config.memory_db_path),
            "midas": Midas(self.message_bus, self.task_manager),
            "adforge": AdForge(self.message_bus),
            "saul_goodman": SaulGoodman(self.message_bus),
            "jarvis_build": JarvisBuild(self.message_bus),
            "ripley": Ripley(self.message_bus),
            "da_vinci": DaVinci(self.message_bus),
            "john_wick": JohnWick(self.message_bus),
        }

        print("[JARVIS] Initializing agents...")
        for name, agent in self.agents.items():
            try:
                await agent.start()
                print(f"  [OK] {agent.name} - {agent.role}")
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")

        self._boot_complete = True
        self._running = True
        print(f"\n[JARVIS] Ecosystem booted successfully!")
        print(f"[JARVIS] {len(self.agents)} agents online")
        print("[JARVIS] Ready to receive commands...\n")

        try:
            from tools.voice_simple import VoiceSystem
            self._voice_system = VoiceSystem()
            self._voice_system.callback = self._on_voice_command

            def _start_voice():
                self._voice_system.run()

            voice_thread = threading.Thread(target=_start_voice, daemon=True, name="Voice-main")
            voice_thread.start()
            print("[JARVIS] Voice system started")
        except ImportError as e:
            print(f"[JARVIS] Voice not available: {e}")
        except Exception as e:
            print(f"[JARVIS] Voice error: {e}")

        await self._status_loop()

    def _on_voice_command(self, command):
        """Handle voice commands from simple voice system."""
        try:
            text = str(getattr(command, "text", "")).strip()
            if not text:
                return
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.execute_command(text))
            else:
                asyncio.ensure_future(self.execute_command(text))
        except Exception:
            return

    async def _status_loop(self):
        """Periodic status broadcast"""
        while self._running:
            await asyncio.sleep(30)
            await self.message_bus.broadcast_heartbeat("orchestra", {
                "agents_online": len([a for a in self.agents.values() if a.is_active]),
                "total_agents": len(self.agents)
            })

    async def shutdown(self):
        """Shutdown all agents gracefully"""
        print("\n[JARVIS] Shutting down ecosystem...")
        self._running = False
        for name, agent in self.agents.items():
            await agent.stop()
        print("[JARVIS] Ecosystem offline")

    def get_status(self) -> Dict[str, Any]:
        """Get ecosystem status"""
        return {
            "running": self._running,
            "boot_complete": self._boot_complete,
            "agents": {name: agent.get_status() for name, agent in self.agents.items()},
            "task_stats": asyncio.create_task(self.task_manager.get_task_stats()) if self._running else None
        }

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a user command through Director Fury"""
        director = self.agents.get("director_fury")
        if director:
            return await director.receive_user_command(command)
        return {"error": "Director Fury not available"}

    async def enable_voice(self) -> Dict[str, Any]:
        """Enable voice control with wake word detection"""
        try:
            from tools.voice_admin import VoiceSystem
            self._voice_system = VoiceSystem()
            voice_ok = await self._voice_system.initialize()

            if voice_ok:
                def _on_voice(vc):
                    try:
                        if getattr(vc, "wake_word_detected", False):
                            return
                        text = str(getattr(vc, "text", "")).strip()
                        if not text:
                            return
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(self.execute_command(text))
                        else:
                            asyncio.ensure_future(self.execute_command(text))
                    except Exception:
                        return

                self._voice_system.set_callback(_on_voice)
                print("[VOICE] Calling enable()...", flush=True)
                self._voice_system.enable()
                print("[VOICE] enable() called, waiting 2s...", flush=True)
                await asyncio.sleep(2)
                print("[VOICE] start_listening should be running now", flush=True)
                self._voice_enabled = True
                print("[JARVIS] Voice control ENABLED - Say 'JARVIS' to activate")
                return {"status": "voice_enabled", "wake_word": "JARVIS"}
            else:
                return {"status": "voice_error", "message": "Voice libraries not available"}
        except ImportError as e:
            return {"status": "voice_error", "message": f"Install voice libraries: {e}"}

    async def disable_voice(self) -> Dict[str, Any]:
        """Disable voice control"""
        if self._voice_system:
            self._voice_system.disable()
            self._voice_enabled = False
            print("[JARVIS] Voice control DISABLED")
        return {"status": "voice_disabled"}

    async def get_pc_status(self) -> Dict[str, Any]:
        """Get PC admin status"""
        try:
            from tools.pc_admin import get_admin_control
            admin = get_admin_control()
            admin.check_admin()
            return admin.get_system_info()
        except Exception as e:
            return {"error": str(e)}

    async def control_pc(self, action: str, target: Optional[str] = None) -> Dict[str, Any]:
        """Execute PC admin action"""
        try:
            from tools.pc_admin import get_admin_control
            admin = get_admin_control()

            if not admin._is_admin:
                return {"error": "Admin privileges required", "hint": "Run as administrator"}

            if action == "processes":
                return await admin.control_process("list")
            elif action == "kill" and target:
                return await admin.control_process("kill", pid=int(target))
            elif action == "services":
                return await admin._get_services()
            elif action == "network":
                return await admin._get_network()
            elif action == "firewall":
                return await admin._get_firewall_status()
            elif action == "shutdown":
                return await admin.system_control("shutdown")
            elif action == "restart":
                return await admin.system_control("restart")
            elif action == "lock":
                return await admin.system_control("lock")
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": str(e)}

    async def edit_registry(self, action: str, path: str, key: str, value: str) -> Dict[str, Any]:
        """Edit Windows registry"""
        try:
            from tools.pc_admin import get_admin_control
            admin = get_admin_control()
            return await admin.registry_edit(action, path, key, value)
        except Exception as e:
            return {"error": str(e)}

    async def self_update(self, mode: str = "full") -> Dict[str, Any]:
        """JARVIS self-update - updates itself when commanded"""
        try:
            from tools.auto_update import get_auto_update
            updater = get_auto_update(self.config.openjarvis_path if hasattr(self.config, 'openjarvis_path') else os.path.dirname(os.path.abspath(__file__)))

            print(f"[JARVIS] Starting self-update (mode: {mode})...")

            if mode == "check":
                return await updater.check_for_updates()
            elif mode == "rollback":
                return await updater.rollback()
            else:
                result = await updater.update(mode)
                print(f"[JARVIS] Self-update completed: {result.get('status')}")
                return result
        except Exception as e:
            return {"error": str(e)}

    async def install_capability(self, capability: str) -> Dict[str, Any]:
        """Install new capability for JARVIS"""
        try:
            from tools.auto_update import get_auto_update
            updater = get_auto_update()
            return await updater.install_new_capability(capability)
        except Exception as e:
            return {"error": str(e)}

    async def restart_jarvis(self) -> Dict[str, Any]:
        """Restart JARVIS system"""
        print("[JARVIS] Restarting...")
        asyncio.create_task(self.shutdown())
        return await get_auto_update().restart()

    async def setup_auto_start(self) -> Dict[str, Any]:
        """Setup JARVIS to start on PC boot"""
        try:
            from tools.auto_start import get_auto_start
            auto_start = get_auto_start()
            result = await auto_start.setup_auto_start()
            print(f"[JARVIS] Auto-start configured: {result}")
            return result
        except Exception as e:
            return {"error": str(e)}

    async def sync_to_github(self) -> Dict[str, Any]:
        """Sync JARVIS + models to GitHub kimikukiu"""
        try:
            from tools.auto_start import get_auto_start
            auto_start = get_auto_start()
            print("[JARVIS] Starting GitHub sync...")
            result = await auto_start.full_sync()
            print(f"[JARVIS] Sync complete: {result}")
            return result
        except Exception as e:
            return {"error": str(e)}

    async def backup_models(self) -> Dict[str, Any]:
        """Backup Ollama models locally"""
        try:
            from tools.auto_start import get_auto_start
            auto_start = get_auto_start()
            result = await auto_start.backup_ollama_models()
            return result
        except Exception as e:
            return {"error": str(e)}

    async def generate_morning_briefing(self) -> Dict[str, Any]:
        """Generate morning briefing with news, weather, risks"""
        try:
            from tools.morning_briefing import get_morning_briefing
            briefing_system = get_morning_briefing()
            briefing = await briefing_system.generate_briefing()
            voice_text = briefing_system.format_briefing_for_voice(briefing)
            return {
                "status": "briefing_generated",
                "briefing": briefing,
                "voice_text": voice_text
            }
        except Exception as e:
            return {"error": str(e)}

    async def post_briefing_to_social(self, platform: str) -> Dict[str, Any]:
        """Post briefing to social media"""
        try:
            from tools.morning_briefing import get_morning_briefing
            briefing_system = get_morning_briefing()
            briefing = await briefing_system.generate_briefing()

            if platform.lower() == "telegram":
                content = briefing_system.format_briefing_for_voice(briefing)
                return await briefing_system.post_to_telegram(content)
            elif platform.lower() == "youtube":
                title = f"Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}"
                content = str(briefing)
                return await briefing_system.post_to_youtube(title, content)
            else:
                return await briefing_system.post_to_social(platform, str(briefing))
        except Exception as e:
            return {"error": str(e)}

    async def set_location(self, city: str, country: str) -> Dict[str, Any]:
        """Set geolocation for weather"""
        from tools.morning_briefing import get_morning_briefing
        briefing = get_morning_briefing()
        briefing.set_location(city, country)
        return {"status": "location_set", "city": city, "country": country}

    async def get_roster(self) -> List[Dict]:
        """Get agent roster"""
        return [
            {
                "name": agent.name,
                "role": agent.role,
                "tier": agent.tier.value,
                "status": agent.status.value,
                "is_busy": agent.is_busy,
                "capabilities": agent.capabilities
            }
            for agent in self.agents.values()
        ]


async def main():
    """Main entry point"""
    orchestra = JARVISOrchestra()

    try:
        api_task = asyncio.create_task(start_api_server(orchestra))
        await asyncio.sleep(0.5)
        await orchestra.boot()
    except KeyboardInterrupt:
        print("\n[JARVIS] Interrupt received")
    finally:
        await orchestra.shutdown()
        try:
            api_task.cancel()
        except Exception:
            pass


def _is_allowed_transcript_folder(folder: str) -> bool:
    if not folder:
        return False
    norm = os.path.normpath(folder).lower()
    return norm.startswith(os.path.normpath(r"d:\jarvis").lower())


async def start_api_server(orchestra: JARVISOrchestra):
    allowed_origins = {"http://localhost:3301", "http://127.0.0.1:3301"}

    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            resp = web.Response(status=204)
        else:
            resp = await handler(request)

        origin = request.headers.get("Origin")
        if origin in allowed_origins:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Access-Control-Allow-Headers"] = "content-type"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return resp

    app = web.Application(middlewares=[cors_middleware])

    async def health(request):
        from tools.uncensored_generator import get_uncensored_generator
        g = get_uncensored_generator()
        return web.json_response({"status": "ok", "ollama": await g.health_check()})

    async def status(request):
        roster = await orchestra.get_roster()
        return web.json_response({"running": True, "agents": roster, "agent_count": len(roster)})

    async def models(request):
        from tools.uncensored_generator import get_uncensored_generator
        g = get_uncensored_generator()
        installed = await g.get_installed_models()
        return web.json_response({
            "installed_models": installed,
            "profiles": g.list_models(),
            "active_model": g.model,
            "num_ctx": g.context_size,
        })

    async def set_model_profile(request):
        from tools.uncensored_generator import get_uncensored_generator
        g = get_uncensored_generator()
        body = await request.json()
        profile = str(body.get("profile", "")).strip().lower()
        return web.json_response(await g.set_profile(profile))

    async def set_model(request):
        from tools.uncensored_generator import get_uncensored_generator
        g = get_uncensored_generator()
        body = await request.json()
        model = str(body.get("model", "")).strip()
        installed = await g.get_installed_models()
        if model not in set(installed):
            return web.json_response({"status": "error", "message": f"Model not installed: {model}", "installed_models": installed}, status=400)
        g.set_model(model)
        return web.json_response({"status": "ok", "active_model": g.model, "num_ctx": g.context_size})

    async def briefing(request):
        return web.json_response(await orchestra.generate_morning_briefing())

    async def money_scan(request):
        from tools.money_maker import get_money_maker
        mm = get_money_maker()
        scan = await mm.scan_all_platforms()
        return web.json_response({"status": "ok", "scan": scan})

    async def ads_generate(request):
        body = await request.json()
        brief = str(body.get("brief") or body.get("text") or "").strip()
        if not brief:
            product = body.get("product")
            audience = body.get("audience")
            offer = body.get("offer")
            platform = body.get("platform")
            brief = f"Product: {product}\nAudience: {audience}\nOffer: {offer}\nPlatform: {platform}".strip()

        context = {
            "type": "ads_generate",
            "language": body.get("language", "ro"),
            "languages": body.get("languages"),
            "brand": body.get("brand"),
            "product": body.get("product"),
            "audience": body.get("audience"),
            "offer": body.get("offer"),
            "platforms": body.get("platforms") or ([body.get("platform")] if body.get("platform") else None),
            "tone": body.get("tone", "direct, pragmatic, premium"),
            "brief": brief,
        }

        try:
            res = await orchestra.execute_command("ads:generate")
            _ = res
        except Exception:
            pass

        try:
            agent = orchestra.agents.get("adforge")
            if agent:
                out = await agent.generate_ads_pack(brief, context)
                return web.json_response({"status": "ok", "result": out})
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=500)

        return web.json_response({"status": "error", "message": "AdForge not available"}, status=500)

    async def social_analyze(request):
        from tools.morning_briefing import get_morning_briefing
        b = get_morning_briefing()
        body = await request.json()
        urls = body.get("urls") or []
        text = body.get("text")
        if (not urls) and text:
            urls = b.extract_urls_from_text(text)
        max_links = int(body.get("max_links", 50))
        analysis = await b.analyze_social_links(urls=urls, max_links=max_links)
        if bool(body.get("generate_content_pack", True)):
            pack = await b.generate_content_pack_for_analysis(
                analysis=analysis,
                language=str(body.get("language", "ro")),
                goal=str(body.get("goal", "educational")),
            )
            return web.json_response({"status": "ok", "analysis": analysis, "content_pack": pack})
        return web.json_response({"status": "ok", "analysis": analysis})

    async def transcripts_analyze(request):
        from tools.morning_briefing import get_morning_briefing
        b = get_morning_briefing()
        body = await request.json()
        transcripts = body.get("transcripts")
        folder = body.get("folder")
        if (not transcripts) and folder:
            folder = str(folder)
            if not _is_allowed_transcript_folder(folder):
                return web.json_response({"status": "error", "message": "Folder not allowed. Use a folder under d:\\jarvis\\..."}, status=400)
            loaded = b.load_transcripts_from_folder(folder, max_files=int(body.get("max_files", 50)))
            transcripts = loaded.get("transcripts", [])

        if not transcripts:
            return web.json_response({"status": "error", "message": "No transcripts provided"}, status=400)

        pack = await b.analyze_transcripts(
            transcripts=transcripts,
            language=str(body.get("language", "ro")),
            goal=str(body.get("goal", "educational")),
            max_tokens=int(body.get("max_tokens", 2500)),
        )
        return web.json_response({"status": "ok", "result": pack})

    async def chat(request):
        from tools.uncensored_generator import get_uncensored_generator
        g = get_uncensored_generator()
        body = await request.json()
        profile = body.get("profile")
        message = str(body.get("message", "")).strip()
        if profile:
            await g.set_profile(str(profile).strip().lower())
        system_prompt = (
            "Ești JARVIS, un asistent AI conversațional, natural și cursiv în limba română. "
            "Răspunzi scurt și clar, dar cald și uman, cu inițiativă. "
            "Când e cazul, pui întrebări de clarificare și propui pași următori concreți. "
            "Prioritizezi decizii legale și sigure și refuzi orice ocolire de securitate sau activități ilegale."
        )
        reply = await g.chat(message, system_prompt=system_prompt)
        return web.json_response({"status": "ok", "model": g.model, "reply": reply})

    async def command(request):
        body = await request.json()
        cmd = str(body.get("command", "")).strip()
        if not cmd:
            return web.json_response({"status": "error", "message": "Missing command"}, status=400)
        res = await orchestra.execute_command(cmd)
        return web.json_response({"status": "ok", "result": res})

    async def autonomy_status(request):
        director = orchestra.agents.get("director_fury")
        if not director:
            return web.json_response({"status": "error", "message": "Director Fury not available"}, status=500)
        try:
            return web.json_response(director.get_autonomy_status())
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    app.router.add_route("GET", "/api/health", health)
    app.router.add_route("OPTIONS", "/api/health", health)
    app.router.add_route("GET", "/api/status", status)
    app.router.add_route("OPTIONS", "/api/status", status)
    app.router.add_route("GET", "/api/models", models)
    app.router.add_route("OPTIONS", "/api/models", models)
    app.router.add_route("POST", "/api/models/profile", set_model_profile)
    app.router.add_route("OPTIONS", "/api/models/profile", set_model_profile)
    app.router.add_route("POST", "/api/models/set", set_model)
    app.router.add_route("OPTIONS", "/api/models/set", set_model)
    app.router.add_route("POST", "/api/briefing", briefing)
    app.router.add_route("OPTIONS", "/api/briefing", briefing)
    app.router.add_route("POST", "/api/money/scan", money_scan)
    app.router.add_route("OPTIONS", "/api/money/scan", money_scan)
    app.router.add_route("POST", "/api/ads/generate", ads_generate)
    app.router.add_route("OPTIONS", "/api/ads/generate", ads_generate)
    app.router.add_route("POST", "/api/social/analyze", social_analyze)
    app.router.add_route("OPTIONS", "/api/social/analyze", social_analyze)
    app.router.add_route("POST", "/api/transcripts/analyze", transcripts_analyze)
    app.router.add_route("OPTIONS", "/api/transcripts/analyze", transcripts_analyze)
    app.router.add_route("POST", "/api/chat", chat)
    app.router.add_route("OPTIONS", "/api/chat", chat)
    app.router.add_route("POST", "/api/command", command)
    app.router.add_route("OPTIONS", "/api/command", command)
    app.router.add_route("GET", "/api/autonomy/status", autonomy_status)
    app.router.add_route("OPTIONS", "/api/autonomy/status", autonomy_status)

    async def monetization_report(request):
        from tools.monetization import get_engine
        engine = get_engine()
        report = engine.get_full_report()
        total = engine.get_all_revenue()
        return web.json_response({"agents": report, "total_revenue": total})

    async def monetization_agent(request):
        agent_id = request.match_info.get("agent_id")
        from tools.monetization import get_engine
        engine = get_engine()
        data = engine.get_agent_data(agent_id)
        return web.json_response(data)

    async def monetization_fetch(request):
        from tools.monetization import get_engine
        engine = get_engine()
        results = engine.fetch_all_data()
        total = engine.get_all_revenue()
        return web.json_response({"status": "ok", "results": results, "total_revenue": total})

    async def monetization_credentials(request):
        from tools.monetization import get_engine
        engine = get_engine()
        if request.method == "POST":
            body = await request.json()
            engine.save_credentials(body)
            return web.json_response({"status": "ok"})
        return web.json_response({"credentials": engine.credentials})

    app.router.add_route("GET", "/api/monetization/report", monetization_report)
    app.router.add_route("OPTIONS", "/api/monetization/report", monetization_report)
    app.router.add_route("GET", "/api/monetization/agent/{agent_id}", monetization_agent)
    app.router.add_route("OPTIONS", "/api/monetization/agent/{agent_id}", monetization_agent)
    app.router.add_route("POST", "/api/monetization/fetch", monetization_fetch)
    app.router.add_route("OPTIONS", "/api/monetization/fetch", monetization_fetch)
    app.router.add_route("GET", "/api/monetization/credentials", monetization_credentials)
    app.router.add_route("POST", "/api/monetization/credentials", monetization_credentials)
    app.router.add_route("OPTIONS", "/api/monetization/credentials", monetization_credentials)

    async def voice_status(request):
        """Get real-time voice status from VoiceSystem"""
        try:
            if (hasattr(orchestra, '_voice_system') and 
                orchestra._voice_system):
                vs = orchestra._voice_system
                status = vs.get_voice_status()
                return web.json_response({
                    "status": status,
                    "speaking": status == "speaking",
                    "listening": status == "listening",
                    "processing": status == "processing",
                    "idle": status == "idle"
                })
            else:
                return web.json_response({
                    "status": "idle",
                    "speaking": False,
                    "listening": False,
                    "processing": False,
                    "idle": True
                })
        except Exception as e:
            print(f"[API] voice_status error: {e}")
            return web.json_response({"error": str(e), "status": "error"})

    async def voice_speak(request):
        body = await request.json()
        text = body.get("text", "")
        if text and hasattr(orchestra, '_voice_system'):
            orchestra._voice_system.speak(text)
            orchestra._voice_system._set_voice_status("speaking")
        return web.json_response({"status": "ok"})

    app.router.add_route("GET", "/api/voice/status", voice_status)
    app.router.add_route("POST", "/api/voice/speak", voice_speak)
    app.router.add_route("OPTIONS", "/api/voice/status", voice_status)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8000)
    await site.start()

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
