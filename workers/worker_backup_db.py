import json
import os
from .loader import register_worker
from logging import getLogger
from ag95 import (configure_logger,
                  SqLiteDbbackup)
from traceback import format_exc

@register_worker(worker_cycle_time_s=6*60*60,
                 worker_name=os.path.basename(__file__))
class Worker:
    def __init__(self):
        self.working = False
        with open('configuration.json', 'r') as f:
            self.config = json.load(f)

        self._log = getLogger(f'{os.path.basename(__file__)}.log')

    def is_working(self):
        return self.working

    def set_working(self):
        self.working = True

    def clear_working(self):
        self.working = False

    def work(self) -> int:
        '''
        The work to execute each cycle
        Returns: an integer which signifies the success of the worker [0,1]
        1 is a bad response, meaning that the worker could not do its job
        0 is a good response, meaning that the worker accomplished its job
        '''
        try:
            SqLiteDbbackup(input_filepath=os.path.join('db', 'database.sqlite'),
                           output_filepath=os.path.join(self.config['db_backup_path'], 'database.sqlite')).backup_db()
            self._log.info('worker completed successfully')
            return 0
        except:
            self._log.error(f'worker failed:\n{format_exc(chain=False)}')
            return 1

if __name__ == '__main__':
    configure_logger(log_name=os.path.join('logs', f'{os.path.basename(__file__)}.log'))
    Worker().work()