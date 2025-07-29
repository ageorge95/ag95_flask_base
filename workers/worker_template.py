from . import register_worker

@register_worker(worker_cycle_time_s=1,
                 worker_name='my_worker_name')
class Worker:
    def __init__(self):
        pass

    def action(self):
        '''
        The action to execute each cycle
        Returns:

        '''
        pass