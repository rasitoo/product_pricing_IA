from collections.abc import Iterable
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.models.llm_metric import LLMMetric


class LLMMetricsService:
    def __init__(self, db: Session):
        self.db = db

    def log_call(self, **kwargs) -> LLMMetric:
        metric = LLMMetric(**kwargs)
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def summarize(self) -> dict:
        rows: Iterable[LLMMetric] = self.db.scalars(select(LLMMetric)).all()
        total_calls = len(rows)
        if total_calls == 0:
            return {
                "total_calls": 0,
                "total_cost_usd": 0.0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "blocked_by_budget": 0,
            }
        total_cost = float(sum(Decimal(str(x.cost_usd)) for x in rows))
        success = len([x for x in rows if x.outcome == "success"])
        blocked = len([x for x in rows if x.outcome == "blocked_by_budget"])
        avg_latency = float(sum(x.latency_ms for x in rows)) / total_calls
        return {
            "total_calls": total_calls,
            "total_cost_usd": round(total_cost, 6),
            "success_rate": round(success / total_calls, 3),
            "avg_latency_ms": round(avg_latency, 2),
            "blocked_by_budget": blocked,
        }
