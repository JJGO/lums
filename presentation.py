import datetime
import time
from typing import Any, Dict, List, Union

import pandas as pd

from gpu import GPU, Error

last_contact = {}


def format_memory(MBs):
    if MBs / 1024 < 1:
        return f"{MBs} MB"
    return f"{MBs/1024:.2f} GB"


def format_time(createtime):
    now = int(time.time())
    return str(datetime.timedelta(seconds=now - createtime))


def server_status(server: str, server_response: Union[Error, List[GPU]]):
    if isinstance(server_response, Error):
        status = {
            Error.CONNECT: "Down",
            Error.TIMEOUT: "Timeout",
        }[server_response]
    else:
        last_contact[server] = int(time.time())
        status = "Up"
    if server in last_contact:
        last_contact_time = format_time(int(time.time()) - last_contact[server])
    else:
        last_contact_time = "Never"
    return {"status": status, "last_contact": last_contact_time}


def gpu_summary(gpu: Dict[str, Any]) -> Dict[str, Any]:
    utilization_intervals = {
        (0, 10): "bg-success",  # green
        (10, 50): "bg-warning",  # yellow
        (50, 101): "bg-danger",  # red
    }

    memory_intervals = {
        (0, 10): "bg-success",  # green
        (10, 75): "bg-warning",  # yellow
        (75, 101): "bg-danger",  # red
    }

    def map_from_intervals(value, intervals):
        for (low, high), style in intervals.items():
            if low <= value < high:
                return style
        raise ValueError("Value outside of intervals")

    gpu["mem_percent"] = int(gpu["memory_used"] / gpu["memory_total"] * 100)
    gpu["n_procs"] = len(gpu["processes"])
    gpu["utilization_style"] = map_from_intervals(
        gpu["utilization"], utilization_intervals
    )
    gpu["memory_style"] = map_from_intervals(gpu["mem_percent"], memory_intervals)
    return gpu


def proc_summary(server: List[GPU]) -> pd.DataFrame:
    columns = ["GPU", "User", "Memory", "Time", "PID"]

    rows = []
    for i, gpu in enumerate(server):
        for p in gpu["processes"]:
            rows.append({"gpu": i, **p})

    if len(rows) == 0:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame.from_records(rows)
    df["GPU"] = df["gpu"]
    df["User"] = df["userid"]
    df["PID"] = df["pid"]
    df["Memory"] = df["used_memory"].map(format_memory)
    df["Time"] = df["createtime"].map(format_time)
    return df[columns]


def website_state(servers):
    states = {}
    for server, response in servers.items():
        state = server_status(server, response)
        if state["status"] == "Up":
            state["gpus"] = [gpu_summary(gpu) for gpu in response]
            state["proc_summary"] = proc_summary(response).to_html(
                index=False, classes="table", border=0
            )
        states[server] = state
    return states
