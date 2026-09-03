import time
import random
import sqlite3
import threading
from contextlib import contextmanager
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, HTTPException, Response

app = FastAPI(title="Orders Service")

DB_PATH = "orders.db"

latency_spike_ms = 0
error_rate = 0.0
db_pool = threading.Semaphore(3)
db_pool_exhausted = False
leaked_memory = []
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["endpoint"])



def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, item TEXT, qty INTEGER)")
    conn.execute("INSERT INTO orders (item, qty) SELECT 'widget', 1 WHERE NOT EXISTS (SELECT 1 FROM orders)")
    conn.commit()
    conn.close()

init_db()

@contextmanager
def get_db_connection():
    acquired = db_pool.acquire(timeout=5)
    if not acquired:
        raise HTTPException(status_code=503, detail="DB connection pool exhausted (timeout waiting for slot)")
    try:
        conn = sqlite3.connect(DB_PATH)
        if db_pool_exhausted:
            time.sleep(2.5)
        yield conn
        conn.close()
    finally:
        db_pool.release()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/orders")
def list_orders():
    start = time.time()

    if latency_spike_ms > 0:
        time.sleep(latency_spike_ms / 1000)

    if random.random() < error_rate:
        REQUEST_COUNT.labels(endpoint="/orders", status="500").inc()
        raise HTTPException(status_code=500, detail="Simulated internal error")

    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, item, qty FROM orders").fetchall()

    REQUEST_COUNT.labels(endpoint="/orders", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/orders").observe(time.time() - start)
    return {"orders": [{"id": r[0], "item": r[1], "qty": r[2]} for r in rows]}



@app.post("/chaos/latency-spike")
def inject_latency():
    global latency_spike_ms
    latency_spike_ms = 1500
    return {"injected": "latency_spike", "extra_ms": latency_spike_ms}


@app.post("/chaos/resolve")
def resolve_all():
    global latency_spike_ms, error_rate, db_pool_exhausted
    latency_spike_ms = 0
    error_rate = 0.0
    db_pool_exhausted = False
    leaked_memory.clear()
    return {"status": "resolved"}

@app.post("/chaos/error-spike")
def inject_errors():
    global error_rate
    error_rate = 0.6
    return {"injected": "error_spike", "rate": error_rate}


@app.post("/chaos/db-pool-exhaust")
def inject_db_pool_exhaustion():
    global db_pool_exhausted
    db_pool_exhausted = True
    return {"injected": "db_pool_exhaustion", "pool_size": 3}


@app.post("/chaos/memory-leak")
def inject_memory_leak():
    leaked_memory.append(bytearray(20 * 1024 * 1024))
    return {"injected": "memory_leak", "chunks_held": len(leaked_memory)}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)