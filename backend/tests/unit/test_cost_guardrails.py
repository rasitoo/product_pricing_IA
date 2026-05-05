from backend.src.services.cost_guardrail_service import CostGuardrailService


def test_cost_guardrails_blocks_when_budget_exceeded():
    svc = CostGuardrailService()
    result = svc.check_budget(10_000)
    assert result.allowed is False
