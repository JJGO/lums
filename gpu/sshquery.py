import getpass
import json

import paramiko
import os
import sys

PYTHONPATH = os.environ['PYTHONPATH']
PYTHON = sys.executable
QUERY = 'from lums.gpu import GPUQuery; import json; print(json.dumps(GPUQuery.instance().run()))'
QUERY_CMD = f"PYTHONPATH={PYTHONPATH} {PYTHON} -c '{QUERY}'"

class SSHQuery:

    def __init__(self, host, ssh_key, known_hosts, user=None, timeout=2):
        self.host = host

        try:
            self.ssh_key = paramiko.Ed25519Key(filename=ssh_key)
        except paramiko.ssh_exception.PasswordRequiredException:
            print(f"Key file {ssh_key} requires a password")
            password = getpass.getpass()
            self.ssh_key = paramiko.Ed25519Key(filename=ssh_key, password=password)

        self.known_hosts = known_hosts

        if user is None:
            user = getpass.getuser()
        self.user = user

        self.timeout = timeout

    def run(self):
        key = paramiko
        with paramiko.SSHClient() as client:
            client.load_host_keys(self.known_hosts)
            client.connect(self.host, username=self.user, pkey=self.ssh_key, timeout=self.timeout)
            try:
                stdin, stdout, stderr = client.exec_command(QUERY_CMD, timeout=self.timeout)
                query = json.loads(stdout.read())
            except paramiko.ssh_exception.PasswordRequiredException:
                query = None
        return query

