import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Account, Decision

_engine = None
_Session = None


def get_session():
    global _engine, _Session
    if _Session is None:
        _engine = create_engine(os.environ["DATABASE_URL"])
        _Session = sessionmaker(bind=_engine)
    return _Session()


def upsert_account(
    account_id: str,
    name: str,
    meta_ad_account: str,
    roas_target: float,
    weekly_budget_ars: float,
    telegram_chat_id: str,
) -> Account:
    session = get_session()
    try:
        account = session.get(Account, account_id)
        if account is None:
            account = Account(id=account_id)
            session.add(account)
        account.name = name
        account.meta_ad_account = meta_ad_account
        account.roas_target = roas_target
        account.weekly_budget_ars = weekly_budget_ars
        account.telegram_chat_id = telegram_chat_id
        session.commit()
        session.refresh(account)
        return account
    finally:
        session.close()


def log_decision(proposal) -> int:
    session = get_session()
    try:
        decision = Decision(
            account_id=proposal.account_id,
            agent_name=proposal.agent_name,
            campaign_id=proposal.campaign_id,
            campaign_name=proposal.campaign_name,
            action=proposal.action,
            reason=proposal.reason,
        )
        session.add(decision)
        session.commit()
        return decision.id
    finally:
        session.close()


def update_decision_status(decision_id: int, status: str):
    session = get_session()
    try:
        decision = session.get(Decision, decision_id)
        if decision is None:
            return None
        decision.status = status
        decision.decided_at = datetime.utcnow()
        session.commit()
        return decision
    finally:
        session.close()


def get_pending_decisions(account_id: str | None = None):
    session = get_session()
    try:
        query = session.query(Decision).filter(Decision.status == "pending")
        if account_id:
            query = query.filter(Decision.account_id == account_id)
        return query.all()
    finally:
        session.close()
