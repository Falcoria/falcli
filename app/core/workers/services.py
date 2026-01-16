import time

from app.connectors.tasker_connector import tasker
from app.messages.errors import Errors
from app.core.workers.models import WorkerIP


def get_workers_ips() -> list[WorkerIP]:
    response = tasker.get_workers_ips()

    if not response.ok:
        raise RuntimeError(Errors.Worker.FAILED_TO_GET_IPS)

    result = response.json()

    if not result or "workers" not in result:
        raise RuntimeError(Errors.Worker.FAILED_TO_GET_IPS)

    def format_ts(ts: int) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts else "unknown"

    ip_data = []
    for hostname, data in result["workers"].items():
        ip = data.get("ip", "unknown")
        last_updated = int(data.get("last_updated", 0))
        last_seen = int(data.get("last_seen", 0))

        last_updated_str = format_ts(last_updated)
        last_seen_str = format_ts(last_seen)

        ip_data.append(WorkerIP(
            hostname=hostname,
            ip=ip,
            last_updated=last_updated_str,
            last_seen=last_seen_str
        ))

    return ip_data

