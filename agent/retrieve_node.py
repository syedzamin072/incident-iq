from state import IncidentState
from retriever import Retriever

_retriever = Retriever()
_loaded = False


def retrieve(state: IncidentState) -> IncidentState:
    global _loaded
    if not _loaded:
        _retriever.load()
        _loaded = True

    results = _retriever.search(state["alert_text"], k=2)
    return {**state, "retrieved": results}


if __name__ == "__main__":
    result = retrieve({"alert_text": "database connection pool timeout errors", "category": "db_pool_exhaustion"})
    for r in result["retrieved"]:
        print(f"{r['score']:.3f} | {r['source']}")