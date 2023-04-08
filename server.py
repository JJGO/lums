# Run with
# uvicorn lums.server:app --host 0.0.0.0 --port PORT

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Union

import aiohttp
from aiohttp import client_exceptions
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings

from gpu import GPU, Error, GPUQuery
from presentation import website_state

PORT = os.environ["PORT"]
DOMAIN = os.environ["DOMAIN"]
SERVERS = os.environ["SERVERS"].split(",")
TIMEOUT = int(os.environ.get('TIMEOUT', '5'))


class Settings(BaseSettings):
    debug: bool = False


log = logging.getLogger("rich")
q = GPUQuery.instance()
settings = Settings()
app = FastAPI(debug=settings.debug)
templates = Jinja2Templates(directory="templates")


@app.get("/gpu", response_model=List[GPU])
def query_gpus():
    return q.run()


async def fetch_gpus(
    session: aiohttp.ClientSession, url: str
) -> Union[List[GPU], Error]:
    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            response = await response.text()
            return json.loads(response)
    except client_exceptions.ClientConnectorError:
        return Error.CONNECT
    except asyncio.exceptions.TimeoutError:
        return Error.TIMEOUT


async def fetch_all_gpus(servers: Dict[str, str]) -> Dict[str, Union[List[GPU], Error]]:
    tasks = []
    async with aiohttp.ClientSession() as session:
        for server, url in servers.items():
            task = asyncio.create_task(fetch_gpus(session, url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        # responses = [r.value if isinstance(r, Error) else r for r in responses]
        return dict(zip(servers, responses))


@app.get("/web", response_class=HTMLResponse)
async def dashboard(request: Request, refresh: int = 0):
    servers = {server: f"http://{server}.{DOMAIN}:{PORT}/gpu" for server in SERVERS}
    responses = await fetch_all_gpus(servers)
    return templates.TemplateResponse(
        "index.html.j2",
        dict(request=request, refresh=refresh, state=website_state(responses)),
    )
    # return await fetch_all_gpus(servers)
