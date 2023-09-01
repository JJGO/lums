# Run with
# uvicorn lums.server:app --host 0.0.0.0 --port PORT

import asyncio
import json
import logging
import os
import threading
import time
from typing import Dict, List, Optional, Union

import aiohttp
import requests
from aiohttp import client_exceptions
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, BaseSettings

from gpu import GPU, Error, GPUQuery
from netdata import NetdataMetrics, netdata_metrics
from presentation import website_state
from storage import Filesystem, get_filesystems

PORT = os.environ["PORT"]
DOMAIN = os.environ["DOMAIN"]
SERVERS = os.environ["SERVERS"].split(",")
TIMEOUT = int(os.environ.get("TIMEOUT", "5"))
HISTORY_INTERVAL = int(os.environ.get("HISTORY_INTERVAL", 60))


class Settings(BaseSettings):
    debug: bool = False


def refresh_api():
    while True:
        response = requests.get(f"http://localhost:{PORT}/api")
        # process the response here
        time.sleep(HISTORY_INTERVAL)


log = logging.getLogger("rich")
q = GPUQuery.instance()
settings = Settings()
app = FastAPI(debug=settings.debug)
templates = Jinja2Templates(directory="templates")

if HISTORY_INTERVAL > 0:
    t = threading.Thread(target=refresh_api)
    t.start()


class APIResult(BaseModel):
    gpus: List[GPU]
    metrics: NetdataMetrics


@app.get("/api", response_model=APIResult)
def query_state():
    return {
        "gpus": q.run(),
        "metrics": netdata_metrics(),
    }


@app.get("/fs", response_model=List[Filesystem])
def query_fs():
    return get_filesystems()


async def fetch(session: aiohttp.ClientSession, url: str) -> Union[APIResult, Error]:
    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            response = await response.text()
            return json.loads(response)
    except client_exceptions.ClientConnectorError:
        return Error.CONNECT
    except asyncio.exceptions.TimeoutError:
        return Error.TIMEOUT


async def fetch_all(servers: Dict[str, str]) -> Dict[str, Union[APIResult, Error]]:
    tasks = []
    async with aiohttp.ClientSession() as session:
        for server, url in servers.items():
            task = asyncio.create_task(fetch(session, url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return dict(zip(servers, responses))


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, refresh: int = 0):
    servers = {server: f"http://{server}.{DOMAIN}:{PORT}/api" for server in SERVERS}
    responses = await fetch_all(servers)
    return templates.TemplateResponse(
        "index.html.j2",
        dict(request=request, refresh=refresh, state=website_state(responses)),
    )


@app.get("/data", response_class=HTMLResponse)
async def fs_dashboard(request: Request):
    servers = {server: f"http://{server}.{DOMAIN}:{PORT}/fs" for server in SERVERS}
    responses = await fetch_all(servers)
    return templates.TemplateResponse(
        "data.html.j2", dict(request=request, state=website_state(responses)),
    )
