from . import register_worker

@register_worker(worker_cycle_time_s=5,
                 worker_name='my_worker_name')
class Worker:
    def __init__(self):
        self.working = False

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
        return 0