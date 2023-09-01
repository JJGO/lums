import subprocess
from typing import List

import jc
from pydantic import BaseModel


class Filesystem(BaseModel):
    name: str
    type: str
    used: int
    available: int


def get_filesystems() -> List[Filesystem]:
    command = ["df", "-T"]
    output_df = subprocess.check_output(command).decode()
    filesystems = jc.parse("df", output_df)

    filtered_filesystems = []
    for filesystem in filesystems:
        if filesystem["type"] in ("tmpfs", "auristorfs"):
            continue
        for name in ("1k_blocks", "filesystem", "use_percent"):
            filesystem.pop(name)
        filesystem["name"] = filesystem.pop("mounted_on")
        filtered_filesystems.append(Filesystem(filesystem))
    return filtered_filesystems
