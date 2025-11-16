import os
import time
import subprocess
import threading
import sys
from . import (load_all_workers,
               WORKERS,
               DO_NOT_RUN_ANY_WORKER_BOOL)
from datetime import datetime
from ag95 import SqLiteDbWrapper
from logging import getLogger

# A thread-safe class to manage the running processes' dictionary.
# This encapsulates the dictionary and protects all access with a lock.
class WorkerManager:
    def __init__(self):
        # A dictionary to hold the subprocess objects, protected by a lock.
        self._running_workers = []
        self._lock = threading.Lock()

    def is_busy(self, worker_name):
        """
        Checks if a worker is currently running.
        This operation is protected by a lock to prevent race conditions.
        """
        with self._lock:
            # if the worker is still active return True
            if worker_name in self._running_workers:
                return True

            # otherwise return False
            return False

    def add_worker(self, worker_name):
        """
        Adds a new worker to the manager's list of running workers.
        This operation is also protected by a lock.
        """
        with self._lock:
            self._running_workers.append(worker_name)

    def remove_worker(self, worker_name):
        """
        Removes a worker from the manager's list of running workers.
        This operation is also protected by a lock.
        """
        with self._lock:
            self._running_workers.remove(worker_name)

# Create a single, thread-safe instance of the manager.
worker_manager = WorkerManager()
_log = getLogger('main')

def _detached_execution(cls):
    """
    Function executed by a new thread to start a worker subprocess.
    """
    worker_name = cls.worker_name
    worker_module = cls.worker_module
    worker_cycle_time_s = cls.worker_cycle_time_s

    worker_manager.add_worker(worker_name)

    try:

        # get the last execution timestamp
        with SqLiteDbWrapper(database_path=os.path.join('db', 'database', 'database.sqlite')) as DB:
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

            _log.info(f'Starting worker process for: {worker_name}')

            p = subprocess.Popen([sys.executable,
                                  '-m',
                                  worker_module],
                                 stdin=subprocess.DEVNULL,
                                 close_fds=True
                                 )
            p.wait()

            exec_return_code = p.returncode
            timestamp_end = datetime.now().timestamp()
            exec_duration_s = round(timestamp_end - timestamp_start,2)
            _log.info(f'Worker process {worker_name} completed in {exec_duration_s}s with'
                      f' {'✅' if exec_return_code == 0 else '❌'} exec_return_code: {exec_return_code}')

            with SqLiteDbWrapper(database_path=os.path.join('db', 'database', 'database.sqlite')) as DB:
                DB.append_in_table(table_name='workers_status',
                                   column_names=['worker_name',
                                                 'exec_timestamp',
                                                 'exec_return_code',
                                                 'exec_duration_s'],
                                   column_values=[worker_name,
                                                  timestamp_end,
                                                  exec_return_code,
                                                  exec_duration_s])

    except Exception as e:
        _log.error(f'Unknown error while running {worker_name}: {e}')

    finally:
        worker_manager.remove_worker(worker_name=worker_name)

def start_workers_relay():
    if DO_NOT_RUN_ANY_WORKER_BOOL:
        return

    # first wait for some time to allow stdin_watcher() to remove a potential leftover exit file
    time.sleep(2)
    load_all_workers()

    while True:
        for cls in WORKERS:
            if not worker_manager.is_busy(cls.worker_name):
                t = threading.Thread(target=_detached_execution,args=(cls,))
                t.start()

        if os.path.isfile('exit'):
            break

        time.sleep(0.5)