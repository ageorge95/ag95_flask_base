import json
import sys
import os
import subprocess
import time
import socket
from server.app import Server
from threading import Thread

def set_terminal_title(title: str):
    if not sys.stdout.isatty() or "PYCHARM_HOSTED" in os.environ:
        return
    sys.stdout.write(f"\033]0;{title}\007")
    sys.stdout.flush()

def wait_for_port(host: str, port: int, timeout: float = 5.0):
    """Poll until the TCP port is accepting connections (or timeout)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False

def start_server():

    t = Thread(target=Server().serve, kwargs=({'port': cfg['server_port']}))
    t.start()

    if wait_for_port('localhost', cfg['server_port'], timeout=10.0):
        print(f"🚀 Server is up at http://localhost:{cfg['server_port']}/")
    else:
        print(f"⚠️  Timeout waiting for port {cfg['server_port']} – the server may not have started correctly.")

    t.join()

def main():

    set_terminal_title(cfg['framework_title'])

    start_server()

if __name__ == "__main__":
    # load config
    with open("configuration.json") as f:
        cfg = json.load(f)

    # start the main method
    main()
