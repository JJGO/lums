from typing import Tuple, List
import psutil

from pynvml.smi import nvidia_smi

from .schema import GPU, Process
from ..util.lru import LRUDict
from ..util.singleton import Singleton


@Singleton
class GPUQuery:
    def __init__(self, cache: int = 256, maxduration: int = 86400):
        self.nv = nvidia_smi()
        self.gpu_count = self.nv.DeviceQuery()["count"]
        # Cache is purged after size limit or time limit
        self.pid_cache = LRUDict(maxsize=cache, maxduration=maxduration)

    def pid_owner_time(self, pid: int) -> Tuple[str, str]:
        if pid not in self.pid_cache:
            process = psutil.Process(pid)
            userid = process.username()
            create_time = process.create_time()
            self.pid_cache[pid] = (userid, create_time)
        return self.pid_cache[pid]

    def run(self) -> List[GPU]:
        query = self.nv.DeviceQuery()
        gpus: List[GPU] = []

        for i in range(self.gpu_count):
            gpu = query["gpu"][i]
            if gpu["processes"] is None:
                gpu["processes"] = []
            for p in gpu["processes"]:
                uid, create_time = self.pid_owner_time(p["pid"])
                p["userid"] = uid
                p["createtime"] = int(create_time)
                del p["process_name"]

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
