import json
import os
from . import register_worker
from ag95 import SqLiteDbbackup

@register_worker(worker_cycle_time_s=6*60*60,
                 worker_name=os.path.basename(__file__))
class Worker:
    def __init__(self):
        self.working = False
        with open('configuration.json', 'r') as f:
            self.config = json.load(f)

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
            return 0
        except:
            return 1