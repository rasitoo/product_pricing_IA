from backend.src.services.clients import ExternalComparableClient, LLMClient


class PricingService:
    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.external_client = ExternalComparableClient()

    async def build_proposal(self, photos: list[dict], query: str) -> dict:
        llm = await self.llm_client.propose(photos)
        comps = await self.external_client.search(query)
        external_prices = [c["price"] for c in comps if c.get("price")]
        avg_external = sum(external_prices) / max(1, len(external_prices))
        suggested_price = round((llm.suggested_price + avg_external) / 2, 2)
        return {
            "description": llm.description,
            "suggested_price": suggested_price,
            "suggested_price_min": round(suggested_price * 0.9, 2),
            "suggested_price_max": round(suggested_price * 1.1, 2),
            "confidence_score": llm.confidence,
            "rationale_internal": {"baseline": llm.suggested_price},
            "rationale_external": {"avg_market_price": round(avg_external, 2), "sources": comps},
        }
