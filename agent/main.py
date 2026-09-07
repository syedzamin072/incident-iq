from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import build_graph

app = FastAPI(title="IncidentIQ Agent")
incident_graph = build_graph()


class AlertPayload(BaseModel):
    alert_text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/diagnose")
def diagnose_incident(payload: AlertPayload):
    if not payload.alert_text.strip():
        raise HTTPException(status_code=400, detail="alert_text cannot be empty")

    result = incident_graph.invoke({"alert_text": payload.alert_text})
    return {
        "category": result.get("category"),
        "diagnosis": result.get("diagnosis"),
        "sources": [c["source"] for c in result.get("retrieved", [])] if result.get("retrieved") else [],
        "cache_hit": result.get("cache_hit", False),
        }