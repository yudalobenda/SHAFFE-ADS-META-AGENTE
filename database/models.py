from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)  # account_id de config/accounts.yaml, ej. "shaffe"
    name = Column(String, nullable=False)
    meta_ad_account = Column(String, nullable=False)
    roas_target = Column(Float, nullable=False)
    weekly_budget_ars = Column(Float, nullable=False)
    telegram_chat_id = Column(String, nullable=False)

    decisions = relationship("Decision", back_populates="account")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    campaign_id = Column(String, nullable=False)
    campaign_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="decisions")
