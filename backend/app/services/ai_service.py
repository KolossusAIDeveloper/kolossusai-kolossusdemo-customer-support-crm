import json
import random
from typing import Optional
from app.config import settings


class AIService:
    def __init__(self):
        self.provider = settings.ai_provider
        self.openai_key = settings.openai_api_key
        self.anthropic_key = settings.anthropic_api_key

    async def score_lead(self, lead_data: dict) -> dict:
        """Score a lead using AI. Returns mock data if no API key configured."""
        if self.provider == "openai" and self.openai_key:
            return await self._score_lead_openai(lead_data)
        elif self.provider == "anthropic" and self.anthropic_key:
            return await self._score_lead_anthropic(lead_data)
        else:
            return self._mock_lead_score(lead_data)

    def _mock_lead_score(self, lead_data: dict) -> dict:
        score = random.randint(30, 95)
        if score >= 70:
            classification = "hot"
        elif score >= 40:
            classification = "warm"
        else:
            classification = "cold"

        return {
            "score": score,
            "classification": classification,
            "intent": "medium_purchase_intent",
            "reasoning": [
                f"Lead from {lead_data.get('source', 'unknown')} source",
                f"Industry: {lead_data.get('industry', 'unknown')}",
                "AI scoring (mock — configure OPENAI_API_KEY for real scoring)"
            ],
            "recommended_action": "Follow up within 24 hours",
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "model_name": "mock",
            "prompt_version": "1.0"
        }

    async def _score_lead_openai(self, lead_data: dict) -> dict:
        try:
            import httpx
            prompt = f"""Analyze this sales lead and provide a JSON score:
Lead: {json.dumps(lead_data, default=str)}

Return JSON with: score (0-100), classification (hot/warm/cold), intent, reasoning (list), recommended_action, confidence (0-1)"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    },
                    timeout=30.0
                )
                data = response.json()
                result = json.loads(data["choices"][0]["message"]["content"])
                result["model_name"] = "gpt-4o-mini"
                result["prompt_version"] = "1.0"
                return result
        except Exception:
            return self._mock_lead_score(lead_data)

    async def _score_lead_anthropic(self, lead_data: dict) -> dict:
        try:
            import httpx
            prompt = f"""Analyze this sales lead and return a JSON score:
Lead: {json.dumps(lead_data, default=str)}

Return JSON with: score (0-100), classification (hot/warm/cold), intent, reasoning (list), recommended_action, confidence (0-1)"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-haiku-5-5",
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30.0
                )
                data = response.json()
                content = data["content"][0]["text"]
                start = content.find("{")
                end = content.rfind("}") + 1
                result = json.loads(content[start:end])
                result["model_name"] = "claude-haiku-5-5"
                result["prompt_version"] = "1.0"
                return result
        except Exception:
            return self._mock_lead_score(lead_data)

    async def summarize_conversation(self, messages: list) -> str:
        text = "\n".join([f"{m.get('sender', 'unknown')}: {m.get('content', '')}" for m in messages])
        return f"Conversation summary: {len(messages)} messages exchanged. Key topics discussed. [AI Summary - configure API key for real summaries]"

    async def suggest_reply(self, conversation_context: str) -> str:
        return "Thank you for reaching out. I'd be happy to help you with your inquiry. Could you please provide more details so I can assist you better? [AI Suggested Reply - configure API key for real suggestions]"


ai_service = AIService()
