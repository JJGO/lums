#!/usr/bin/env python
# Run with
# uvicorn lums.server:app --host 0.0.0.0 --port PORT 

import logging
from typing import List

from fastapi import FastAPI
from pydantic import BaseSettings

from rich.traceback import install

from lums.gpu import GPUQuery
from lums.gpu.schema import GPU


class Settings(BaseSettings):
    debug: bool = False


log = logging.getLogger("rich")
q = GPUQuery.instance()
settings = Settings()
app = FastAPI(debug=settings.debug)


@app.get("/gpu", response_model=List[GPU])
def query_gpus():
    return q.run()
