import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi

from utils.logger import get_logger

logger = get_logger(__name__)


class MetaAdsClient:
    def __init__(self, app_id: str, app_secret: str, access_token: str, ad_account_id: str):
        FacebookAdsApi.init(app_id, app_secret, access_token)
        self.ad_account_id = ad_account_id
        self.account = AdAccount(ad_account_id)

    def get_active_campaigns(self) -> list[dict]:
        campaigns = self.account.get_campaigns(
            fields=[Campaign.Field.id, Campaign.Field.name, Campaign.Field.status, Campaign.Field.objective],
            params={"effective_status": ["ACTIVE"]},
        )
        return [
            {
                "id": c[Campaign.Field.id],
                "name": c[Campaign.Field.name],
                "status": c[Campaign.Field.status],
                "objective": c[Campaign.Field.objective],
            }
            for c in campaigns
        ]

    def get_campaign_insights(self, date_preset: str = "last_7d") -> list[dict]:
        """Trae métricas reales por campaña. Si Meta no devuelve datos de compras,
        se marca has_purchase_data=False en vez de inventar un ROAS."""
        insights = self.account.get_insights(
            fields=[
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.campaign_name,
                AdsInsights.Field.spend,
                AdsInsights.Field.purchase_roas,
                AdsInsights.Field.ctr,
                AdsInsights.Field.impressions,
            ],
            params={"level": "campaign", "date_preset": date_preset},
        )
        results = []
        for row in insights:
            purchase_roas = row.get(AdsInsights.Field.purchase_roas)
            roas = float(purchase_roas[0]["value"]) if purchase_roas else 0.0
            results.append({
                "campaign_id": row.get(AdsInsights.Field.campaign_id),
                "campaign_name": row.get(AdsInsights.Field.campaign_name),
                "spend": float(row.get(AdsInsights.Field.spend, 0)),
                "roas": roas,
                "ctr": float(row.get(AdsInsights.Field.ctr, 0)),
                "impressions": int(row.get(AdsInsights.Field.impressions, 0)),
                "has_purchase_data": purchase_roas is not None,
            })
        return results

    def test_connection(self) -> bool:
        info = self.account.api_get(fields=["name", "account_status", "currency"])
        logger.info(
            f"Conectado a cuenta Meta Ads: {info.get('name')} ({self.ad_account_id}) "
            f"- status={info.get('account_status')} currency={info.get('currency')}"
        )
        return True


def _client_from_env() -> MetaAdsClient:
    return MetaAdsClient(
        app_id=os.environ["META_APP_ID"],
        app_secret=os.environ["META_APP_SECRET"],
        access_token=os.environ["META_ACCESS_TOKEN"],
        ad_account_id=os.environ["META_AD_ACCOUNT_ID"],
    )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        client = _client_from_env()
        client.test_connection()
        campaigns = client.get_active_campaigns()
        logger.info(f"Campañas activas encontradas: {len(campaigns)}")
        for c in campaigns:
            logger.info(f"  - {c['name']} ({c['id']}) [{c['status']}]")
