import json

import requests

class HTTPQuery:

    def __init__(self, host, port, timeout=2):
        self.url = f"http://{host}:{port}/gpu"

    def run(self):
        try:
            r = requests.get(self.url, timeout=2)
            return r.json()
        except requests.exceptions.ReadTimeout:
            return {}
