import os
import json
import hashlib
import redis
from state import IncidentState

_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
CACHE_TTL_SECONDS = 300


def _make_cache_key(state: IncidentState) -> str:
    raw = f"{state.get('category', 'unknown')}"
    return "incidentiq:diag:" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def check_cache(state: IncidentState) -> IncidentState:
    key = _make_cache_key(state)
    cached = _client.get(key)

    if cached:
        payload = json.loads(cached)
        return {**state, "diagnosis": payload["diagnosis"], "sources": payload["sources"], "cache_hit": True}

    return {**state, "cache_hit": False}


def write_cache(state: IncidentState) -> IncidentState:
    key = _make_cache_key(state)
    payload = json.dumps({
        "diagnosis": state["diagnosis"],
        "sources": [c["source"] for c in state.get("retrieved", [])],
    })
    _client.setex(key, CACHE_TTL_SECONDS, payload)
    return state


def route_after_cache(state: IncidentState) -> str:
    return "respond" if state.get("cache_hit") else "diagnose"