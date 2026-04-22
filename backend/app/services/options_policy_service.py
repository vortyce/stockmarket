from sqlalchemy.orm import Session
from app.repositories.options_repo import OptionsRepository
from app.models.options import OptionsPolicyConfig
from typing import Dict, Any

class OptionsPolicyService:
    def __init__(self, db: Session):
        self.repo = OptionsRepository(db)

    def get_current_policy(self) -> OptionsPolicyConfig:
        """
        Returns the active operational policy. 
        If none exists, the repository initializes the default.
        """
        return self.repo.get_active_policy()

    def update_policy(self, updates: Dict[str, Any]) -> OptionsPolicyConfig:
        policy = self.get_current_policy()
        return self.repo.update_policy(policy.id, updates)

    @staticmethod
    def get_default_policy_values() -> Dict[str, Any]:
        """
        Reference values from the PRD for initialization/reset.
        """
        return {
            "min_dte": 7,
            "max_dte": 45,
            "exit_dte": 21,
            "profit_target_pct": 0.50,
            "covered_call_delta_min": 0.15,
            "covered_call_delta_max": 0.25,
            "cash_put_delta_min": 0.15,
            "cash_put_delta_max": 0.25,
            "min_open_interest": 300,
            "min_bid": 0.15,
            "max_spread_pct": 0.20
        }
