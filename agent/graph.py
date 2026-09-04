from langgraph.graph import StateGraph, END
from state import IncidentState
from classify_node import classify
from retrieve_node import retrieve


def build_graph():
    graph = StateGraph(IncidentState)

    graph.add_node("classify", classify)
    graph.add_node("retrieve", retrieve)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"alert_text": "database connection pool timeout errors"})
    print(result)