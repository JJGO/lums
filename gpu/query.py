import time
import datetime
import psutil

from pynvml.smi import nvidia_smi

from ..util.lru import LRUDict
from ..util.singleton import Singleton

@Singleton
class GPUQuery:

    def __init__(self, cache=64):
        self.nv = nvidia_smi()
        self.gpu_count = self.nv.DeviceQuery()['count']
        self.pid_cache = LRUDict(maxsize=cache)

    def pid_owner_time(self, pid):
        # TODO: Cleanup the cache overtime
        if pid not in self.pid_cache:
            process = psutil.Process(pid)
            userid = process.username()
            create_time = process.create_time()
            self.pid_cache[pid] = (userid, create_time)
        return self.pid_cache[pid]

    def run(self):
        query = self.nv.DeviceQuery()
        gpus = []
        procs = []
        now = time.time()

        for i in range(self.gpu_count):
            gpu = query['gpu'][i]
            if gpu['processes'] is None:
                gpu['processes'] = []
            for p in gpu['processes']:
                uid, create_time = self.pid_owner_time(p['pid'])
                p['userid'] = uid
                p['createtime'] = int(create_time)
                del p['process_name']

            gpus.append({
                "memory_total": gpu['fb_memory_usage']['total'],
                "memory_used": gpu['fb_memory_usage']['used'],
                "memory_free": gpu['fb_memory_usage']['free'],
                "utilization": gpu['utilization']['gpu_util'],
                "temperature": gpu['temperature']['gpu_temp'],
                "model": gpu['product_name'],
                "processes": gpu['processes'],
                "n_proc": len(gpu['processes']),
            })
        return gpus



