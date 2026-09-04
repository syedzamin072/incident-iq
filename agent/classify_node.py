from state import IncidentState

_CATEGORY_KEYWORDS = {
    "db_pool_exhaustion": ["pool", "connection", "timeout"],
    "latency_spike": ["latency", "slow", "p95"],
    "error_spike": ["error rate", "500", "failing"],
    "memory_leak": ["memory", "leak", "oom"],
}


def classify(state: IncidentState) -> IncidentState:
    text = state["alert_text"].lower()

    category = "unknown"
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            category = cat
            break

    return {**state, "category": category}

if __name__ == "__main__":
    result = classify({"alert_text": "database connection pool timeout errors"})
    print(result)