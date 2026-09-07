from langgraph.graph import StateGraph, END
from state import IncidentState
from classify_node import classify
from retrieve_node import retrieve
from diagnose_node import diagnose
from cache_node import check_cache, write_cache, route_after_cache
from guardrail_node import guardrail_check


def respond(state: IncidentState) -> IncidentState:
    return state


def build_graph():
    graph = StateGraph(IncidentState)

    graph.add_node("classify", classify)
    graph.add_node("check_cache", check_cache)
    graph.add_node("retrieve", retrieve)
    graph.add_node("diagnose", diagnose)
    graph.add_node("write_cache", write_cache)
    graph.add_node("respond", respond)
    graph.add_node("guardrail", guardrail_check)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "check_cache")

    graph.add_conditional_edges(
        "check_cache",
        route_after_cache,
        {"respond": "guardrail", "diagnose": "retrieve"},
    )

    graph.add_edge("retrieve", "diagnose")
    graph.add_edge("diagnose", "write_cache")
    graph.add_edge("write_cache", "guardrail")
    graph.add_edge("guardrail", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"alert_text": "database connection pool timeout errors"})
    print("cache_hit:", result.get("cache_hit"))
    print("diagnosis:", result.get("diagnosis"))