import random
from dataclasses import dataclass

import httpx


@dataclass
class LLMResult:
    description: str
    suggested_price: float
    confidence: float


class LLMClient:
    async def propose(self, _: list[dict]) -> LLMResult:
        return LLMResult(
            description="Producto en buen estado, apto para venta de segunda mano.",
            suggested_price=round(random.uniform(20, 120), 2),
            confidence=0.82,
        )


class ExternalComparableClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=10)

    async def search(self, query: str) -> list[dict]:
        return [
            {"source": "market-a", "url": f"https://example.com/{query}", "price": 59.99},
            {"source": "market-b", "url": f"https://example.org/{query}", "price": 62.50},
        ]
