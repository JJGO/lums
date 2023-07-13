import requests
from pydantic import BaseModel
import psutil

total_memory_mib = psutil.virtual_memory().total / 1024 ** 2
num_cores = psutil.cpu_count(logical=True)


class NetdataMetrics(BaseModel):
    cpu: float
    ram: float
    network_down: float
    network_up: float
    disk_read: float
    disk_write: float


def netdata_metrics(interval_seconds: int = 60) -> NetdataMetrics:
    options = {
        "chart": "system.cpu,system.ram,system.load,system.net,system.io",
        "after": f"-{interval_seconds:d}",
        "points": 1,
        "group": "average",
        "time_group": "average",
        "format": "json",
        "options": "jsonwrap",
    }
    url = "http://localhost:19999/api/v1/data"
    r = requests.get(url, params=options).json()
    metrics = {
        chart + "." + metric: value
        for chart, metric, value in zip(
            r["chart_ids"], r["result"]["labels"][1:], r["result"]["data"][0][1:]
        )
    }
    # from checking the api/v1/charts, we know that system.io and system.net are in Kb/s
    return {
        "cpu": round(sum(v for k, v in metrics.items() if k.startswith('system.cpu.')), 1),
        "ram": round(metrics["system.ram.used"] / total_memory_mib * 100, 1),
        "network_down": round(metrics["system.net.received"] / 1024, 2),
        "network_up": round(-metrics["system.net.sent"] / 1024, 2),
        "disk_read": round(metrics["system.io.in"] / 1024, 2),
        "disk_write": round(-metrics["system.io.out"] / 1024, 2),
    }
