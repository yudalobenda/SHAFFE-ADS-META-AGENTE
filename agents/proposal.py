from dataclasses import dataclass, field


@dataclass
class Proposal:
    account_id: str
    agent_name: str
    campaign_id: str
    campaign_name: str
    action: str  # "pausar" | "escalar" | "mantener" | "redistribuir"
    reason: str
    metrics: dict = field(default_factory=dict)
