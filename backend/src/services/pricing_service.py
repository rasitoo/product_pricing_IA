from backend.src.services.clients import ExternalComparableClient, LLMClient


class PricingService:
    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.external_client = ExternalComparableClient()

    async def build_proposal(
        self,
        photos: list[dict],
        query: str = "",
        context: dict | None = None,
    ) -> dict:
        """Generate an AI pricing proposal.

        Args:
            photos: list of dicts with keys 'filename', optionally 'content_base64'
                    and/or 'storage_uri'.
            query: fallback search query when the LLM does not produce keywords.
            context: enrichment dict with optional keys:
                - 'feedback_signals': recent human corrections to learn from
                - 'historical_refs': past sales in our platform
                Web prices are fetched automatically using LLM-generated keywords.
        """
        ctx = context or {}

        # Step 1: LLM analysis (vision + context-aware prompt)
        # Web prices are not yet available here; they will be fetched after
        # the LLM returns product keywords.
        llm = await self.llm_client.propose(photos, context=ctx)

        # Step 2: Web search using LLM-generated keywords (or fallback query)
        search_query = " ".join(llm.product_keywords) if llm.product_keywords else query
        web_comps = await self.external_client.search(search_query)

        # Step 3: Blend prices — LLM 60%, market 40%
        market_prices = [c["price"] for c in web_comps if c.get("price")]
        hist_prices = [
            h["sold_price"]
            for h in ctx.get("historical_refs", [])
            if h.get("sold_price")
        ]
        all_external = market_prices + hist_prices

        if all_external:
            avg_external = sum(all_external) / len(all_external)
            suggested = round(llm.suggested_price * 0.6 + avg_external * 0.4, 2)
        else:
            avg_external = llm.suggested_price
            suggested = round(llm.suggested_price, 2)

        return {
            "description": llm.description,
            "suggested_price": suggested,
            "suggested_price_min": round(suggested * 0.85, 2),
            "suggested_price_max": round(suggested * 1.15, 2),
            "confidence_score": llm.confidence,
            "rationale_internal": {
                "llm_estimate": llm.suggested_price,
                "product_keywords": llm.product_keywords,
                "feedback_signals_used": len(ctx.get("feedback_signals", [])),
                "historical_refs_used": len(hist_prices),
            },
            "rationale_external": {
                "avg_market_price": round(avg_external, 2),
                "web_sources_found": len(market_prices),
                "sources": web_comps[:5],
            },
        }
