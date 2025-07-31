import os
import time

from . import (load_all_workers,
               WORKERS,
               DO_NOT_RUN_ANY_WORKER_BOOL)
from datetime import datetime
from ag95 import SqLiteDbWrapper
from threading import Thread
from logging import getLogger

def _detached_execution(worker):
    # mark the worker as in_work
    worker.set_working()

    _log = getLogger('main')

    worker_name = worker.worker_name
    worker_cycle_time_s = worker.worker_cycle_time_s

    # get the last execution timestamp
    with SqLiteDbWrapper(database_path=os.path.join('db', 'database.sqlite')) as DB:
        query_result = DB.return_records(table_name='workers_status',
                                         where_statement=f"worker_name == '{worker_name}'",
                                         limit=1,
                                         order='DESC')
    if query_result:
        worker__last_exec_timestamp = query_result[0][1]
    else:
        worker__last_exec_timestamp = 0

    # is it time to run the worker ?
    timestamp_start = datetime.now().timestamp()
    if (timestamp_start - worker__last_exec_timestamp) > worker_cycle_time_s:

        _log.info(f'Started worker thread for: {worker_name}')

        success = worker.work()
        timestamp_end = datetime.now().timestamp()
        exec_duration_s = round(timestamp_end - timestamp_start,2)
        _log.info(f'Worker thread {worker_name} completed in {exec_duration_s}s with status: {success}')

        with SqLiteDbWrapper(database_path=os.path.join('db', 'database.sqlite')) as DB:
            DB.append_in_table(table_name='workers_status',
                               column_names=['worker_name',
                                             'exec_timestamp',
                                             'exec_success',
                                             'exec_duration_s'],
                               column_values=[worker_name,
                                              timestamp_end,
                                              success,
                                              exec_duration_s])
    # mark the worker as free
    worker.clear_working()

def start_workers_relay():
    if DO_NOT_RUN_ANY_WORKER_BOOL:
        return

    # first wait for some time to allow stdin_watcher() to remove a potential leftover exit file
    time.sleep(2)

    load_all_workers()

    while True:
        for worker in WORKERS:
            if not worker.is_working():
                t = Thread(target=_detached_execution, args=(worker,))
                t.start()

        if os.path.isfile('exit'):
            break

        time.sleep(0.5)