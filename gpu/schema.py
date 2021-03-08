from typing import List

from pydantic import BaseModel


class Process(BaseModel):
    pid: int
    unit: str
    used_memory: int
    userid: str
    createtime: int


class GPU(BaseModel):

    memory_free: int
    memory_total: int
    memory_used: int
    model: str
    utilization: float
    temperature: int
    processes: List[Process]
