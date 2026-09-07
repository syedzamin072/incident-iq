import os
from dotenv import load_dotenv
from google import genai
from state import IncidentState

load_dotenv()
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_INSTRUCTION = """You are an incident diagnosis assistant. Follow these rules:
1. Base your diagnosis ONLY on the provided context below. Do not invent causes not supported by it.
2. If the context does not clearly cover this situation, say so explicitly rather than guessing.
3. Respond in two short parts labeled exactly "Diagnosis:" and "Suggested fix:"."""


def diagnose(state: IncidentState) -> IncidentState:
    retrieved = state.get("retrieved", [])

    if not retrieved:
        return {
            **state,
            "diagnosis": "No similar past incident found. Recommend manual investigation.",
        }

    context_str = "\n\n".join(f"[{c['source']}] {c['text']}" for c in retrieved)
    prompt = f"{SYSTEM_INSTRUCTION}\n\nAlert: {state['alert_text']}\n\nContext:\n{context_str}\n\nProvide the diagnosis now."

    response = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    return {**state, "diagnosis": response.text}


if __name__ == "__main__":
    test_state = {
        "alert_text": "database connection pool timeout errors",
        "retrieved": [
            {"source": "db-pool-exhaustion.md", "text": "A surge in concurrent requests exhausted the database connection pool."}
        ],
    }
    result = diagnose(test_state)
    print(result["diagnosis"])