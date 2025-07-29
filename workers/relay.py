from . import WORKERS

def start():
    print([_.worker_name for _ in WORKERS])