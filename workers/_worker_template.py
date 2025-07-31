import os
from ._loader import register_worker
from ._bootstrap import WorkerBootstrap
from logging import getLogger
from ag95 import configure_logger
from traceback import format_exc

# @register_worker(worker_cycle_time_s=5,
#                  worker_name=os.path.basename(__file__))
class Worker(WorkerBootstrap):
    def __init__(self):
        super().__init__()

        # get a log instance
        self._log = getLogger(f'{os.path.basename(__file__)}.log')

    def work(self) -> int:
        '''
        The work to execute each cycle
        Returns: an integer which signifies the success of the worker [0,1]
        1 is a bad response, meaning that the worker could not do its job
        0 is a good response, meaning that the worker accomplished its job
        '''
        try:
            self._log.info('I did something')

            self._log.info('worker completed successfully')
            return 0
        except:
            self._log.error(f'worker failed:\n{format_exc(chain=False)}')
            return 1

if __name__ == '__main__':
    configure_logger(log_name=os.path.join('logs', f'{os.path.basename(__file__)}.log'))
    Worker().work()