import json
from typing import List

import requests
from pydantic import parse_obj_as

from .schema import GPU


class HTTPQuery:
    def __init__(self, host, port, timeout=2):
        self.url = f"http://{host}:{port}/gpu"

    def run(self):
        try:
            r = requests.get(self.url, timeout=2)
            return parse_obj_as(List[GPU], r.json())
        except requests.exceptions.ReadTimeout:
            return {}
