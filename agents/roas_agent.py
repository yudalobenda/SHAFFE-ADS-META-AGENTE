from agents.proposal import Proposal
from connectors.meta_ads_api import MetaAdsClient
from utils.logger import get_logger

logger = get_logger(__name__)


class ROASAgent:
    def __init__(self, client: MetaAdsClient, account_id: str, roas_target: float, date_preset: str = "last_7d"):
        self.client = client
        self.account_id = account_id
        self.roas_target = roas_target
        self.date_preset = date_preset

    def run(self) -> list[Proposal]:
        insights = self.client.get_campaign_insights(date_preset=self.date_preset)
        proposals = []
        for row in insights:
            if not row["has_purchase_data"]:
                logger.info(
                    f"Sin datos de compras para campaña {row['campaign_name']} ({row['campaign_id']}) "
                    "- se omite del análisis de ROAS"
                )
                continue

            roas = row["roas"]
            if roas < self.roas_target * 0.5:
                action = "pausar"
                reason = f"ROAS {roas:.2f}x está muy por debajo del target {self.roas_target:.2f}x"
            elif roas < self.roas_target:
                action = "mantener"
                reason = f"ROAS {roas:.2f}x por debajo del target {self.roas_target:.2f}x pero no crítico"
            elif roas >= self.roas_target * 1.5:
                action = "escalar"
                reason = f"ROAS {roas:.2f}x supera holgadamente el target {self.roas_target:.2f}x"
            else:
                action = "mantener"
                reason = f"ROAS {roas:.2f}x en línea con el target {self.roas_target:.2f}x"

            proposals.append(Proposal(
                account_id=self.account_id,
                agent_name="roas_agent",
                campaign_id=row["campaign_id"],
                campaign_name=row["campaign_name"],
                action=action,
                reason=reason,
                metrics={"roas": roas, "spend": row["spend"], "ctr": row["ctr"]},
            ))
        return proposals
