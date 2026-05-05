class AutoapprovalPolicyService:
    def is_enabled(self) -> bool:
        return False

    def evaluate(self, confidence: float) -> dict:
        return {
            "eligible": confidence >= 0.95,
            "enabled": self.is_enabled(),
            "decision": "manual_review_required",
        }
