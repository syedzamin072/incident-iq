EVAL_CASES = [
    {"alert_text": "database connection pool timeout errors", "expected_category": "db_pool_exhaustion"},
    {"alert_text": "p95 latency spike on orders endpoint", "expected_category": "latency_spike"},
    {"alert_text": "error rate above 25% on orders service", "expected_category": "error_spike"},
    {"alert_text": "memory usage climbing steadily, possible leak", "expected_category": "memory_leak"},
    {"alert_text": "connections timing out waiting for pool slot", "expected_category": "db_pool_exhaustion"},
    {"alert_text": "requests failing with 500 errors consistently", "expected_category": "error_spike"},
]