from collections import deque
from enum import Enum
from typing import Any, Dict, List, Tuple

import numpy as np

import psutil
from pydantic import BaseModel

from helpers import LRUDict, Singleton

# All flags are under pynvml.smi.NVSMI_QUERY_GPU (very unintuitive names)
QUERY = "memory.free, memory.total, memory.used, utilization.memory, utilization.gpu, temperature.gpu, compute-apps, count, gpu_name"

HISTORY_SIZE = 20


class Process(BaseModel):
    pid: int
    unit: str
    used_memory: int
    userid: str
    createtime: int
    is_jupyter: bool
    mean_utilization: float


class GPU(BaseModel):

    memory_free: int
    memory_total: int
    memory_used: int
    model: str
    utilization: float
    temperature: int
    processes: List[Process]


@Singleton
class GPUQuery:
    def __init__(self):  # , cache: int = 256, maxduration: int = 86400):
        from pynvml.smi import nvidia_smi

        self.nv = nvidia_smi()
        self.gpu_count = self.nv.DeviceQuery(QUERY)["count"]
        # Cache is purged after size limit or time limit
        # self.pid_cache = LRUDict(maxsize=cache, maxduration=maxduration)
        self.gpu_utilization_history = [deque() for _ in range(self.gpu_count)]

    def pid_owner_time(self, pid: int) -> Tuple[str, str]:
        if pid not in self.pid_cache:
            process = psutil.Process(pid)
            userid = process.username()
            create_time = process.create_time()
            self.pid_cache[pid] = (userid, create_time)
        return self.pid_cache[pid]

    def pid_properties(self, pid: int) -> Dict[str, Any]:
        process = psutil.Process(pid)
        return {
            "userid": process.username(),
            "createtime": int(process.create_time()),
            "is_jupyter": "ipykernel_launcher" in process.cmdline(),
            # "status": process.status(),
        }

    def run(self) -> List[GPU]:
        query = self.nv.DeviceQuery(QUERY)
        gpus: List[GPU] = []

        for i in range(self.gpu_count):
            gpu = query["gpu"][i]

            utilization_history = self.gpu_utilization_history[i]
            current_utilization = gpu["utilization"]["gpu_util"]
            utilization_history.append(current_utilization)
            if len(utilization_history) > HISTORY_SIZE:
                utilization_history.popleft()

            if gpu["processes"] is None:
                gpu["processes"] = []
            for p in gpu["processes"]:
                p.update(self.pid_properties(p["pid"]))
                del p["process_name"]

                p["mean_utilization"] = np.mean(utilization_history)

            processes = [Process(**p) for p in gpu["processes"]]

            gpus.append(
                GPU(
                    memory_total=gpu["fb_memory_usage"]["total"],
                    memory_used=gpu["fb_memory_usage"]["used"],
                    memory_free=gpu["fb_memory_usage"]["free"],
                    model=gpu["product_name"],
                    utilization=gpu["utilization"]["gpu_util"],
                    temperature=gpu["temperature"]["gpu_temp"],
                    processes=processes,
                )
            )
        return gpus


class Error(str, Enum):
    TIMEOUT = "timeout error"
    CONNECT = "connection error"
