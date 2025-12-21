import os
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

class MyServiceBackend(metaclass=Singleton_without_cache):
    def __init__(self):
        pass

    @staticmethod
    def do_something():
        return 'i did a thing'

@register_worker(worker_cycle_time_s=5,
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

            MyServiceBackend()

            service = Flask(__name__)

            @service.route('/get_some_backend_data')
            def get_inverter_status():

                return MyServiceBackend().do_something()

            serve(service,
                  host='127.0.0.1' if LOCALHOST_ONLY else '0.0.0.0',
                  port=8911,
                  threads=5)

            self._log.info('Service closed successfully')
            return 0
        except:
            self._log.error(f'Service failed:\n{format_exc(chain=False)}')
            return 1

if __name__ == '__main__':
    exit(Worker().work())