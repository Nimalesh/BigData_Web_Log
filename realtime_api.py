from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

app = FastAPI(title="Realtime Log Anomaly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(host="localhost", port=6379, db=0)

@app.get("/logs/", summary="Get most recent logs")
def get_recent_logs(limit: int = 50, anomaly_only: bool = False):
    logs = r.lrange("realtime_logs", 0, limit-1)
    logs = [json.loads(l) for l in logs]
    if anomaly_only:
        logs = [log for log in logs if log.get("is_anomaly") == -1]
    return logs

@app.get("/stats/", summary="Get anomaly statistics")
def get_stats():
    logs = r.lrange("realtime_logs", 0, 999)
    logs = [json.loads(l) for l in logs]
    anomaly = sum(1 for log in logs if log.get("is_anomaly") == -1)
    normal = len(logs) - anomaly
    return {"anomaly": anomaly, "normal": normal}
