import time
from pydantic import BaseModel, Field


class WorkerIP(BaseModel):
    hostname: str
    ip: str
    last_updated: str
    last_seen: str


class WorkerIPView(BaseModel):
    hostname: str
    ip: str
    last_updated: str
    last_seen_ago: str = Field(default="unknown")

    @staticmethod
    def from_worker_ip(worker_ip: WorkerIP) -> "WorkerIPView":
        def _delta_ago(ts_str: str) -> str:
            try:
                ts = time.mktime(time.strptime(ts_str, "%Y-%m-%d %H:%M:%S"))
                delta_sec = int(time.time()) - int(ts)
                if delta_sec < 60:
                    return f"{delta_sec} sec ago"
                elif delta_sec < 3600:
                    return f"{delta_sec // 60} min ago"
                else:
                    return f"{delta_sec // 3600} h ago"
            except Exception:
                return "unknown"

        return WorkerIPView(
            hostname=worker_ip.hostname,
            ip=worker_ip.ip,
            last_updated=worker_ip.last_updated,
            last_seen_ago=_delta_ago(worker_ip.last_seen),
        )