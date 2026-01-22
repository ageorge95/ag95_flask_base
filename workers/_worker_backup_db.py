import os
from ._loader import register_worker
from ._bootstrap import WorkerBootstrap
from logging import getLogger
from ag95 import (configure_logger,
                  SqLiteDbWrapperServiceClient)
from traceback import format_exc

@register_worker(worker_cycle_time_s=6*60*60,
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

            computer_name = os.environ['COMPUTERNAME'].lower()
            output_folderpath = self.config.get()['db_backup_path'].replace('$$COMPUTER_NAME$$', computer_name)

            with SqLiteDbWrapperServiceClient(port=self.config.get(reload=True)['db_ops_port']) as client:
                client.backup_db(output_filepath=os.path.join(output_folderpath, 'database.sqlite'))

            self._log.info('worker completed successfully')
            return 0
        except:
            self._log.error(f'worker failed:\n{format_exc(chain=False)}')
            return 1

if __name__ == '__main__':
    exit(Worker().work())