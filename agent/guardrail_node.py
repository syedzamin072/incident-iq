import re
from state import IncidentState

_DESTRUCTIVE_PATTERNS = [
    r"\bdrop\s+table\b",
    r"\bdelete\s+from\b",
    r"\brm\s+-rf\b",
    r"\btruncate\b",
    r"\bforce[-\s]?kill\b",
]


def guardrail_check(state: IncidentState) -> IncidentState:
    diagnosis_text = (state.get("diagnosis") or "").lower()
    flagged = any(re.search(pattern, diagnosis_text) for pattern in _DESTRUCTIVE_PATTERNS)

    if flagged:
        safe_diagnosis = (
            "⚠️ The generated diagnosis included a potentially destructive suggested action "
            "and has been withheld pending human review. Please investigate this incident manually."
        )
        return {**state, "guardrail_flagged": True, "diagnosis": safe_diagnosis}

    return {**state, "guardrail_flagged": False}

if __name__ == "__main__":
    safe = guardrail_check({"diagnosis": "Increase the connection pool size."})
    print("Safe case flagged:", safe["guardrail_flagged"])

    unsafe = guardrail_check({"diagnosis": "Suggested fix: DROP TABLE orders and recreate it."})
    print("Unsafe case flagged:", unsafe["guardrail_flagged"])