from typing import TypedDict, Optional


class IncidentState(TypedDict, total=False):
    alert_text: str
    category: str
    retrieved: list[dict]
    diagnosis: Optional[str]
    cache_hit: bool
    guardrail_flagged: bool