import time

import typer

import rich
from rich.traceback import install

install(show_locals=True)

from rich.table import Table
from rich.console import Console
from rich.progress_bar import ProgressBar
from rich.panel import Panel
from rich.live import Live
from rich import box

from .gpu import GPUQuery
from .gpu.stats import proc_summary
from .gpu import ParallelQuery, HTTPQuery


def format_gpu_stats(query):

    gpu_table = Table(
        box=box.SIMPLE_HEAD, width=60, padding=(0, 0), collapse_padding=True
    )
    gpu_table.add_column("GPU", justify="right")
    gpu_table.add_column("Util", justify="right")
    gpu_table.add_column("Memory")
    gpu_table.add_column("Use", justify="right")
    gpu_table.add_column("Total", justify="right")
    gpu_table.add_column("ºC", justify="right")

    for i, gpu in enumerate(query):
        style = "green"
        mem_frac = gpu.memory_used / gpu.memory_total
        if mem_frac > 0.2:
            style = "yellow"
        if mem_frac > 0.8 or len(gpu.processes) >= 2 or gpu.utilization > 50:
            style = "red"
        bar = ProgressBar(gpu.memory_total, gpu.memory_used, complete_style=style)
        mem_used = f"{gpu.memory_used/1024:.1f}"
        mem_total = f"{gpu.memory_total/1024:.1f}"
        util = f"{gpu.utilization:.0f}%"
        num = str(i)
        temp = str(int(gpu.temperature))
        gpu_table.add_row(num, util, bar, mem_used, mem_total, temp)

    procs = proc_summary(query).to_dict(orient="records")
    proc_table = Table(
        box=box.SIMPLE_HEAD, width=35, padding=(0, 0), collapse_padding=True
    )
    proc_table.add_column("GPU", justify="right")
    proc_table.add_column("User")
    proc_table.add_column("Mem (MiB)", justify="right")
    proc_table.add_column("PID", justify="right")

    for p in procs:
        gpu = str(p["gpu"])
        user = p["userid"]
        pid = str(p['pid'])
        memory = f'{p["used_memory"]:,}'
        proc_table.add_row(gpu, user, memory, pid)

    parent_table = Table.grid()
    parent_table.add_row(gpu_table, "   ", proc_table)

    return parent_table


def gpu_stats():
    qs = {
        server: HTTPQuery(server, 42007)
        for server in ("oreo", "mars", "twix", "milo", "ahoy")
    }
    parallel = ParallelQuery(qs)
    queries = parallel.run()

    stats = Table.grid()

    for server, query in queries.items():
        table = format_gpu_stats(query)
        # title = f"[bright_blue]{server.upper()}[/bright_blue]"
        # panel = Panel.fit(
        #     table, title=title, padding=(0, 0), border_style="bright_black"
        # )
        # stats.add_row(panel)
        table.title = server.upper()
        stats.add_row(table)
    return stats


def main(
    refresh: int = typer.Option(0, "-r", "--refresh"),
):
    console = Console()
    if refresh == 0:
        console.print(gpu_stats())
    else:
        console.clear()
        with Live(gpu_stats(), refresh_per_second=1, auto_refresh=False) as live:
            while True:
                time.sleep(refresh)
                live.update(gpu_stats())


if __name__ == "__main__":
    typer.run(main)
