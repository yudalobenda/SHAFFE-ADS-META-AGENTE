from agents.proposal import Proposal
from utils.logger import get_logger

logger = get_logger(__name__)


class BudgetAgent:
    """Redistribuye presupuesto desde campañas a pausar hacia campañas a escalar,
    usando solo el spend real reportado por el ROASAgent (nunca inventa montos)."""

    def __init__(self, account_id: str, weekly_budget_ars: float):
        self.account_id = account_id
        self.weekly_budget_ars = weekly_budget_ars

    def run(self, roas_proposals: list[Proposal]) -> list[Proposal]:
        escalar = [p for p in roas_proposals if p.action == "escalar"]
        pausar = [p for p in roas_proposals if p.action == "pausar"]

        if not pausar or not escalar:
            return []

        spend_to_free = sum(p.metrics.get("spend", 0) for p in pausar)
        if spend_to_free <= 0:
            return []

        share = spend_to_free / len(escalar)
        proposals = []
        for p in escalar:
            proposals.append(Proposal(
                account_id=self.account_id,
                agent_name="budget_agent",
                campaign_id=p.campaign_id,
                campaign_name=p.campaign_name,
                action="redistribuir",
                reason=(
                    f"Reasignar ~${share:,.0f} ARS liberados de campañas pausadas "
                    "hacia esta campaña de buen desempeño"
                ),
                metrics={"budget_increase_ars": share},
            ))
        return proposals
