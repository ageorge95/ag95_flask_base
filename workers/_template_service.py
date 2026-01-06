import os
import threading
import time
from ._loader import register_worker
from ._bootstrap import WorkerBootstrap
from logging import getLogger
from ag95 import (configure_logger,
                  Singleton_without_cache)
from traceback import format_exc
from waitress import serve
from flask import Flask

SERVICE_PORT = 8911
LOCALHOST_ONLY = True

def exit_file_watcher(log, exit_flag_func, action):
    while True:
        if exit_flag_func():
            log.info(f"Exit command detected.")
            action()
            break
        time.sleep(1)

class MyServiceBackend(metaclass=Singleton_without_cache):
    def __init__(self):
        pass

    @staticmethod
    def do_something():
        return 'i did a thing'

# @register_worker(worker_cycle_time_s=0,
#                  worker_name=os.path.basename(__file__).replace('.py', ''))
class Worker(WorkerBootstrap):
    def __init__(self):
        super().__init__()

        # get a log instance
        configure_logger(log_name=os.path.join('logs', f'{os.path.basename(__file__)}.log'),
                         backupCount=5,
                         log_level='INFO')
        self._log = getLogger(f'{os.path.basename(__file__)}.log')

    def work(self) -> int:
        '''
        The work to execute each cycle
        Returns: an integer which signifies the success of the worker [0,1]
        1 is a bad response, meaning that the worker could not do its job
        0 is a good response, meaning that the worker accomplished its job
        '''
        try:
            self._log.info('Starting service ...')

            # Create an event to signal the main service thread to exit
            stop_event = threading.Event()

            def handle_shutdown():
                # Here you could have a call to MyServiceBackend().shutdown() if needed
                stop_event.set()  # Signals the loop below to stop

            MyServiceBackend()

            service = Flask(__name__)

            @service.route('/get_some_backend_data')
            def get_some_backend_data():
                return MyServiceBackend().do_something()

            # start exit file watcher
            watcher = threading.Thread(
                target=exit_file_watcher,
                args=(self._log, self.should_exit, handle_shutdown),
                daemon=True
            )
            watcher.start()

            # Start Waitress in a DAEMON thread so it doesn't block the exit
            server_thread = threading.Thread(
                target=serve,
                kwargs={
                    'app': service,
                    'host': '127.0.0.1' if LOCALHOST_ONLY else '0.0.0.0',
                    'port': SERVICE_PORT,
                    'threads': 5
                },
                daemon=True
            )
            server_thread.start()

            # Keep this thread alive until handle_shutdown is called
            while not stop_event.is_set():
                stop_event.wait(timeout=1.0)

            self._log.info('Service closed successfully')
            return 0
        except:
            self._log.error(f'Service failed:\n{format_exc(chain=False)}')
            return 1

if __name__ == '__main__':
    exit(Worker().work())