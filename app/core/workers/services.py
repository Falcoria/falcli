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

    ip_data = []
    for hostname, data in result["workers"].items():
        ip = data.get("ip", "unknown")
        last_updated = data.get("last_updated", 0)

        last_updated_str = (
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_updated))
            if last_updated else "unknown"
        )

        ip_data.append(WorkerIP(
            hostname=hostname,
            ip=ip,
            last_updated=last_updated_str
        ))

    return ip_data
