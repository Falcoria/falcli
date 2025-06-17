import time
from pydantic import BaseModel, Field


class WorkerIP(BaseModel):
    hostname: str
    ip: str
    last_updated: str


class WorkerIPView(WorkerIP):
    last_updated_ago: str = Field(default="unknown")

    @staticmethod
    def from_worker_ip(worker_ip: WorkerIP) -> "WorkerIPView":
        # Parse last_updated string back to timestamp:
        try:
            ts = time.mktime(time.strptime(worker_ip.last_updated, '%Y-%m-%d %H:%M:%S'))
            delta_sec = int(time.time()) - int(ts)
            if delta_sec < 60:
                ago = f"{delta_sec} sec ago"
            elif delta_sec < 3600:
                ago = f"{delta_sec // 60} min ago"
            else:
                ago = f"{delta_sec // 3600} h ago"
        except Exception:
            ago = "unknown"

        return WorkerIPView(
            hostname=worker_ip.hostname,
            ip=worker_ip.ip,
            last_updated=worker_ip.last_updated,
            last_updated_ago=ago
        )