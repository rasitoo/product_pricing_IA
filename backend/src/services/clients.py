import base64
import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from openai import AsyncOpenAI

from backend.src.config.settings import get_settings


@dataclass
class LLMResult:
    description: str
    suggested_price: float
    confidence: float
    product_keywords: list[str] = field(default_factory=list)


class LLMClient:
    """OpenAI gpt-4o vision client for product analysis and pricing."""

    _STUB_DESCRIPTIONS = [
        "Artículo en buen estado general, con signos leves de uso. Ideal para segunda mano.",
        "Producto bien conservado, funcionando correctamente. Oportunidad de compra.",
        "Buen estado de conservación, sin daños relevantes. Listo para usar.",
    ]

    def __init__(self) -> None:
        self.settings = get_settings()

    def _load_image_b64(self, storage_uri: str) -> str | None:
        path = Path(storage_uri)
        if path.exists():
            return base64.b64encode(path.read_bytes()).decode()
        return None

    def _build_system_prompt(self, context: dict) -> str:
        lines = [
            "Eres un experto en valoración de productos de segunda mano para una plataforma de reventa en España.",
            "Analiza las imágenes del producto y genera una descripción atractiva en español y un precio de venta sugerido en EUR.",
            "",
            "Responde ÚNICAMENTE con JSON válido (sin bloques markdown) con exactamente estos campos:",
            '{"description": "...", "suggested_price": 0.00, "confidence": 0.85, "product_keywords": ["..."]}',
            "",
            "Instrucciones:",
            "- description: 2-3 frases en español, describen el producto, su estado y atractivo para el comprador",
            "- suggested_price: precio realista de venta en EUR como número decimal",
            "- confidence: tu nivel de confianza en la valoración entre 0.0 y 1.0",
            "- product_keywords: 3-5 palabras clave en español para buscar comparables de precio en internet",
        ]

        # Feedback signals: learn from human operator corrections
        feedback = context.get("feedback_signals", [])
        if feedback:
            lines.append("")
            lines.append("## CORRECCIONES DE OPERADORES HUMANOS (aprende de estos patrones):")
            for f in feedback[-15:]:
                field_label = "descripción" if f["field_name"] == "description_text" else "precio"
                orig = str(f["original_value"])[:100]
                corr = str(f["corrected_value"])[:100]
                lines.append(f"  - {field_label}: IA propuso '{orig}' → operador corrigió a '{corr}'")
            lines.append("  → Ajusta tus respuestas para evitar estos tipos de errores.")

        # Historical references from our own platform
        hist = context.get("historical_refs", [])
        if hist:
            lines.append("")
            lines.append("## VENTAS HISTÓRICAS EN NUESTRA PLATAFORMA (referencia de precios reales):")
            for h in hist[:8]:
                cond = h.get("condition_label") or "sin clasificar"
                sim = h.get("similarity_score")
                sim_txt = f", similitud {sim:.0%}" if sim else ""
                lines.append(f"  - Vendido a {h['sold_price']:.2f}€ (condición: {cond}{sim_txt})")

        # Web search results
        web = context.get("web_prices", [])
        if web:
            valid = [w for w in web if w.get("price")]
            if valid:
                avg = sum(w["price"] for w in valid) / len(valid)
                lines.append("")
                lines.append(f"## PRECIOS EN MERCADO ONLINE (media: {avg:.2f}€):")
                for w in valid[:6]:
                    title = w.get("title", "")[:60]
                    lines.append(f"  - {w['price']:.2f}€ — {title}")

        return "\n".join(lines)

    async def propose(self, photos: list[dict], context: dict | None = None) -> LLMResult:
        ctx = context or {}

        if self.settings.llm_stub or not self.settings.openai_api_key:
            return LLMResult(
                description=random.choice(self._STUB_DESCRIPTIONS),
                suggested_price=round(random.uniform(20, 120), 2),
                confidence=0.50,
                product_keywords=["producto", "segunda mano"],
            )

        # Build image content blocks (max 9, gpt-4o limit)
        image_blocks: list[dict] = []
        for photo in photos[:9]:
            b64 = None
            if photo.get("content_base64"):
                raw = photo["content_base64"]
                b64 = raw.split(",", 1)[1] if "," in raw else raw
            elif photo.get("storage_uri"):
                b64 = self._load_image_b64(photo["storage_uri"])
            if b64:
                image_blocks.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"},
                })

        user_content: list[dict] = [
            {"type": "text", "text": "Analiza este producto y responde con el JSON solicitado."},
            *image_blocks,
        ]
        if not image_blocks:
            user_content.append({"type": "text", "text": "(Sin imágenes disponibles — usa tu criterio general.)"})

        from openai import AuthenticationError, APIStatusError
        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._build_system_prompt(ctx)},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=600,
                response_format={"type": "json_object"},
                timeout=self.settings.llm_request_timeout_seconds,
            )
        except (AuthenticationError, APIStatusError):
            return LLMResult(
                description=random.choice(self._STUB_DESCRIPTIONS),
                suggested_price=round(random.uniform(20, 120), 2),
                confidence=0.50,
                product_keywords=["producto", "segunda mano"],
            )

        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)

        return LLMResult(
            description=str(parsed.get("description", "Producto de segunda mano.")),
            suggested_price=float(parsed.get("suggested_price", 50.0)),
            confidence=min(1.0, max(0.0, float(parsed.get("confidence", 0.7)))),
            product_keywords=list(parsed.get("product_keywords", [])),
        )


class ExternalComparableClient:
    """Search for comparable product prices using DuckDuckGo (no API key needed)."""

    _PRICE_RE = re.compile(r"(\d{1,5}(?:[.,]\d{1,2})?)\s*(?:€|EUR|eur)\b", re.IGNORECASE)

    async def search(self, query: str) -> list[dict]:
        if not query or query.strip() in ("", "generic-product"):
            return []
        try:
            return await self._search_ddg(query)
        except Exception:
            return []

    async def _search_ddg(self, query: str) -> list[dict]:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS  # type: ignore[no-redef]

        search_query = f"{query} precio comprar segunda mano"
        results: list[dict] = []

        # DDGS is sync; run in threadpool via asyncio.to_thread
        import asyncio

        def _sync_search() -> list[dict]:
            ddg = DDGS()
            return list(ddg.text(search_query, max_results=15))

        raw_results = await asyncio.to_thread(_sync_search)

        for item in raw_results:
            snippet = (item.get("body") or "") + " " + (item.get("title") or "")
            prices_found = self._PRICE_RE.findall(snippet)
            for price_str in prices_found:
                try:
                    price = float(price_str.replace(",", "."))
                    if 1.0 <= price <= 15_000.0:
                        results.append({
                            "source": item.get("href", ""),
                            "url": item.get("href", ""),
                            "title": (item.get("title") or "")[:120],
                            "price": price,
                        })
                        break  # one price per result
                except ValueError:
                    continue

        return results
