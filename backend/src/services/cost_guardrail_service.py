from dataclasses import dataclass

from backend.src.config.settings import get_settings


@dataclass
class CostGuardrailResult:
    allowed: bool
    reason: str | None = None


class CostGuardrailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def check_budget(self, current_daily_cost_usd: float) -> CostGuardrailResult:
        if current_daily_cost_usd >= self.settings.llm_daily_budget_usd:
            return CostGuardrailResult(allowed=False, reason="daily_budget_exceeded")
        return CostGuardrailResult(allowed=True)
