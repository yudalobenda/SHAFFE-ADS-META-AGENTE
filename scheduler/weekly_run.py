import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from dotenv import load_dotenv

from agents.budget_agent import BudgetAgent
from agents.roas_agent import ROASAgent
from agents.telegram_agent import build_summary_message, send_proposals
from connectors.meta_ads_api import MetaAdsClient
from database import queries
from utils.logger import get_logger

logger = get_logger(__name__)


def load_accounts(path: str = "config/accounts.yaml") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["accounts"]


def run_account(account: dict, dry_run: bool) -> None:
    client = MetaAdsClient(
        app_id=os.environ["META_APP_ID"],
        app_secret=os.environ["META_APP_SECRET"],
        access_token=os.environ["META_ACCESS_TOKEN"],
        ad_account_id=account["meta_ad_account"],
    )

    roas_agent = ROASAgent(client, account_id=account["id"], roas_target=account["roas_target"])
    roas_proposals = roas_agent.run()

    budget_agent = BudgetAgent(account_id=account["id"], weekly_budget_ars=account["weekly_budget_ars"])
    budget_proposals = budget_agent.run(roas_proposals)

    all_proposals = roas_proposals + budget_proposals

    if dry_run:
        logger.info("\n" + build_summary_message(account["name"], all_proposals))
        return

    queries.upsert_account(
        account_id=account["id"],
        name=account["name"],
        meta_ad_account=account["meta_ad_account"],
        roas_target=account["roas_target"],
        weekly_budget_ars=account["weekly_budget_ars"],
        telegram_chat_id=account["telegram_chat_id"],
    )

    asyncio.run(send_proposals(
        bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        chat_id=account["telegram_chat_id"],
        proposals=all_proposals,
    ))


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="No envía Telegram ni escribe en la base de datos")
    args = parser.parse_args()

    accounts = load_accounts()
    for account in accounts:
        logger.info(f"Procesando cuenta: {account['name']}")
        run_account(account, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
