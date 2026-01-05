import json
import sys
import os
import time
import socket
import logging
import glob
from traceback import format_exc
from server.app import Server
from workers._relay import start_workers_relay
from db.structure import database_structure
from threading import Thread
from multiprocessing import Process
from ag95 import (stdin_watcher,
                  configure_logger,
                  SqLiteDbMigration)

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

def _start_server_slave(port):
    Server().serve(port=port)

def _start_server_watcher(server_process):
    # first wait for some time to allow stdin_watcher() to remove a potential leftover exit file
    time.sleep(2)

    while True:
        if os.path.isfile('exit'):
            server_process.terminate()
            _log.info('Server closed gracefully')
            return
        time.sleep(0.5)

def start_server():

    p = Process(target=_start_server_slave,
                kwargs={'port': cfg['server_port']})
    p.start()
    _log.info(f"Server launched in detached PID {p.pid}")

    check_server_started()

    t = Thread(target=_start_server_watcher, args=(p,))
    t.start()

def check_server_started():
    if wait_for_port('localhost', cfg['server_port'], timeout=10.0):
        _log.info(f"🚀 Server is up at http://localhost:{cfg['server_port']}/")
    else:
        _log.info(f"⚠️  Timeout waiting for port {cfg['server_port']} – the server may not have started correctly.")

def start_workers():
    t = Thread(target=start_workers_relay)
    t.start()

def start_stdin_watcher():

    stdin_watcher(
        trigger_command='exit',
        init_action=(lambda: [os.remove(f) for f in glob.glob('exit*') if os.path.isfile(f)]),
        trigger_action=(lambda: open('exit', 'w'))
    )

def initialize_db():
    SqLiteDbMigration(database_path=os.path.join('db', 'database', 'database.sqlite'),
                      all_tables_def=database_structure).migrate()

def main():

    set_terminal_title(cfg['framework_title'])

    initialize_db()

    start_server()

    start_workers()

    start_stdin_watcher()

if __name__ == "__main__":
    # load config
    with open("configuration.json") as f:
        cfg = json.load(f)

    # configure the main logger
    configure_logger(log_name=os.path.join('logs', 'main.log'))
    _log = logging.getLogger('main')

    # start the main method
    try:
        main()
    except:
        _log.error(f"Uncaught exception in main():{format_exc(chain=False)}")
