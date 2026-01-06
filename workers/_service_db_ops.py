import os
import time
import threading
from ._loader import register_worker
from ._bootstrap import WorkerBootstrap
from logging import getLogger
from ag95 import (configure_logger,
                  initialize_SqliteDbWrapper_service)
from traceback import format_exc

def exit_file_watcher(log, exit_flag_func, action):
    while True:
        if exit_flag_func():
            log.info(f"Exit command detected.")
            action()
            break
        time.sleep(1)

@register_worker(worker_cycle_time_s=0,
                 worker_name=os.path.basename(__file__).replace('.py', ''))
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

            # start exit file watcher
            watcher = threading.Thread(
                target=exit_file_watcher,
                args=(self._log, self.should_exit, handle_shutdown),
                daemon=True
            )
            watcher.start()

            # Start Waitress in a DAEMON thread so it doesn't block the exit
            server_thread = threading.Thread(
                target=initialize_SqliteDbWrapper_service,
                kwargs={
                    'LOCALHOST_ONLY': True,
                    'SERVICE_PORT': self.config.get(reload=True)['db_ops_port'],
                    'database_path': os.path.join('db', 'database', 'database.sqlite'),
                    'timeout': 5*60,
                    'shutdown_watcher_mode': "none"
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