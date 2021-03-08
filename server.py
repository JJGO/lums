#!/usr/bin/env python

import logging
from typing import List

from fastapi import FastAPI
from pydantic import BaseSettings

import rich
from rich.logging import RichHandler
from rich.traceback import install

from lums.gpu import GPUQuery
from lums.gpu.schema import GPU


class Settings(BaseSettings):
    debug: bool = False


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
q = GPUQuery.instance()
settings = Settings()
app = FastAPI(debug=settings.debug)


@app.get("/gpu", response_model=List[GPU])
def query_gpus():
    return q.run()
