import json
import os
from . import register_worker
from ..db.structure import database_structure
from ag95 import SqLiteDbWrapper

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
            with SqLiteDbWrapper(database_path='db/database.db') as DB:
                for table_def in database_structure:
                    table_name = table_def['table_name']
                    max_history_s = table_def['max_history_s']

                    DB.clear_old_records(table_name=table_name,
                                         since_time_in_past_s=max_history_s)
            return 0
        except:
            return 1