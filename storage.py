import subprocess
from typing import List, Dict

import jc
import pandas as pd
from pydantic import BaseModel
from humanize import naturalsize


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
        filtered_filesystems.append(Filesystem(**filesystem))
    return filtered_filesystems


def group_filesystems(data: Dict[str, Filesystem]):
    IGNORED = ("/boot/efi", "/boot", "/var/cache/openafs", "/storage")
    groups = {}
    for server, filesystems in data.items():
        for filesystem in filesystems:
            name = filesystem["name"]
            if name in IGNORED:
                continue
            elif name == '/local' and filesystem['type'] == 'zfs':
                continue
            elif name.startswith("/data/ddmg"):
                group = "TIG NFS"
            elif name.startswith("/storage"):
                group = "Oats NFS"
            else:
                group = server
            if group not in groups:
                groups[group] = {}
            if name == "/mnt/hdd":
                name = "/local"
                filesystem["name"] = "/local"
            groups[group][name] = filesystem
    return {
        "TIG NFS": groups["TIG NFS"],
        **{name: groups[name] for name in data},
        "Oats NFS": groups["Oats NFS"],
    }


def storage_groups(data):
    storage_groups = {}
    for group, filesystems in group_filesystems(data).items():
        df = pd.DataFrame.from_records(list(filesystems.values()))
        df["size"] = df["used"] + df["available"]
        df["use percent"] = round(df["used"] / df["size"] * 100, 1)
        df.drop(columns=["type"], inplace=True)

        for col in ("size", "used", "available"):
            # df returns data in KiB
            df[col] = (df[col] * 1024).map(naturalsize)

        storage_groups[group] = df.to_dict("records")
    return storage_groups
