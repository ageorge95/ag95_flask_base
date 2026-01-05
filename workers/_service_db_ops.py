import os
from ._loader import register_worker
from ._bootstrap import WorkerBootstrap
from logging import getLogger
from ag95 import (configure_logger,
                  initialize_SqliteDbWrapper_service)
from traceback import format_exc

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

            initialize_SqliteDbWrapper_service(LOCALHOST_ONLY=True,
                                               SERVICE_PORT=self.config.get(reload=True)['db_ops_port'],
                                               database_path=os.path.join('db', 'database', 'database.sqlite'),
                                               timeout=5*60,
                                               shutdown_watcher_mode="wait_for_exit_file")

            # the only way to gracefully close the service is with a SIGTERM, so the code should never reach this code
            # but, it is still here for consistency
            self._log.info('Service closed successfully')
            return 0
        except:
            self._log.error(f'Service failed:\n{format_exc(chain=False)}')
            return 1

if __name__ == '__main__':
    exit(Worker().work())