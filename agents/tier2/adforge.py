import asyncio
from typing import Dict, Any, List

from core.agent_base import Tier2Agent
from core.types import AgentTier, AgentStatus, Message, MessageType
from core.message_bus import MessageBus
from tools.uncensored_generator import get_uncensored_generator


class AdForge(Tier2Agent):
    def __init__(self, message_bus: MessageBus):
        super().__init__(
            name="AdForge",
            role="Ads + Copywriting + Campaign Strategy",
            tier=AgentTier.TIER_2_SPECIALIST,
            message_bus=message_bus,
            capabilities=[
                "ad_copywriting",
                "campaign_planning",
                "creative_briefs",
                "hooks_headlines_cta",
                "brand_voice",
                "landing_page_copy",
                "compliance_sanity_check",
            ]
        )

    async def initialize(self) -> bool:
        print(f"[{self.name}] Initializing ads and copywriting protocols...")
        self.status = AgentStatus.ACTIVE
        return True

    async def process_message(self, message: Message) -> Any:
        if message.msg_type == MessageType.TASK:
            return await self.execute_task(message.content)
        elif message.msg_type == MessageType.BROADCAST:
            if message.content.get("action") == "status_request":
                return self.get_status()
        return None

    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        task = task_data.get("task", "") or ""
        context = task_data.get("context", {}) or {}

        if context.get("type") == "ads_generate" or task.lower().startswith("ads:"):
            brief = context.get("brief") or task
            return await self.generate_ads_pack(brief, context)

        if any(k in task.lower() for k in ["reclam", "ads", "ad ", "copy", "headline", "hook", "cta", "campanie", "campaign", "landing"]):
            return await self.generate_ads_pack(task, context)

        return {"status": "ignored", "message": "Not an ads task"}

    async def generate_ads_pack(self, brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
        generator = get_uncensored_generator()
        try:
            await generator.set_profile("balanced")
        except Exception:
            pass

        languages: List[str] = []
        if isinstance(context.get("languages"), list):
            languages = [str(x).strip() for x in context.get("languages") if str(x).strip()]
        if not languages:
            languages = [str(context.get("language", "ro")).strip() or "ro"]

        payload = {
            "task": "ads_generate",
            "languages": languages,
            "brief": brief,
            "brand": context.get("brand"),
            "product": context.get("product"),
            "audience": context.get("audience"),
            "offer": context.get("offer"),
            "platforms": context.get("platforms", ["tiktok", "instagram", "facebook", "youtube", "google"]),
            "tone": context.get("tone", "direct, pragmatic, premium"),
            "constraints": {
                "no_deceptive_claims": True,
                "no_fake_results": True,
                "no_impersonation": True,
                "include_clear_cta": True,
                "keep_it_specific": True,
            },
            "deliverables": [
                "creative_brief",
                "10_hooks",
                "10_headlines",
                "10_primary_texts",
                "5_offer_angles",
                "landing_page_outline",
                "video_script_30s",
                "video_script_60s",
                "compliance_checklist",
            ],
        }

        system_prompt = (
            "Ești un director de marketing și copywriter senior. "
            "Scrii reclame foarte bune, clare și persuasive, dar fără minciuni, promisiuni false sau înșelăciuni. "
            "Dacă lipsesc informații critice, pui 3 întrebări scurte înainte de execuție."
        )

        system_prompt = system_prompt + " Livrează output-ul structurat pe limbi, cu secțiuni clare pentru fiecare platformă."
        text = await generator.chat(message=str(payload), system_prompt=system_prompt)
        return {"status": "ok", "model": generator.model, "output": text}
