# LUMS: Lightweight Uncomplicated Monitoring System

![](https://raw.githubusercontent.com/JJGO/lums/assets/lums-screenshot.png)

Lums monitors shared computing infrastructure and presents state in a neat and clean web frontend.

## Installation

You can install `lums` by cloning it and installing dependencies
<!-- in two ways:

- **With pip**:

```shell
pip install git+https://github.com/JJGO/lums.git
```

- **Manually**: --> 

```shell
git clone https://github.com/JJGO/lums
python -m pip install -r ./lums/requirements.txt
```


## Quickstart

To run `lums` you need to specify `PORT`, `SERVERS` and `DOMAIN` environment variables, e.g.

```shell
export PORT=42222
export SERVERS=foo,bar
export DOMAIN=example.com
python -m uvicorn server:app --port $PORT --host 0.0.0.0  --reload
```

You need to run `lums` on each server that is part of the cluster. Then navigating to http://server.example.com:42222/

#### API

`lums` also provides a JSON API that you can access at http://server.example.com:42222/api

## Deployment

Lums is best run as a host service as it needs to query the unix ids for the user running processes. Here's a systemd template that you can place at `/etc/systemd/system/lums.service`

```
# /etc/systemd/system/lums.service
[Unit]
Description=LUMS Server
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=10
User=myuser
Environment=PORT=42222
Environment=SERVERS=foo,bar,baz
Environment=DOMAIN=example.com
WorkingDirectory=/home/myuser
ExecStart=/home/myuser/env/bin/python -m uvicorn server:app --port "$PORT" --host 0.0.0.0

[Install]
WantedBy=multi-user.target
```

Then

```shell
sudo systemctl daemon-reload
sudo systemctl restart lums
```

If you want CPU and RAM statistics install [Netdata](https://github.com/netdata/netdata) & [psutil](https://github.com/giampaolo/psutil) and ensure it's available at port 19999.

## Tech Stack

- [PyNVML](https://github.com/gpuopenanalytics/pynvml) - To query GPU state
- [Netdata](https://github.com/netdata/netdata) & [psutil](https://github.com/giampaolo/psutil) - For server metrics like CPU and RAM utilization
- [FastAPI](https://github.com/tiangolo/fastapi) & [uvicorn](https://github.com/encode/uvicorn) - For the backend
- [Pydantic](https://github.com/pydantic/pydantic/) - For schema and data validation
- [Jinja](https://github.com/pallets/jinja) - For Templating
