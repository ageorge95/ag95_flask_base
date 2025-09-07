import importlib
import pkgutil
from pathlib import Path

WORKERS = []

def register_worker(_cls=None,
                    *,
                    worker_cycle_time_s,
                    worker_name):
    def decorator(cls):

        # attach metadata
        cls.worker_cycle_time_s = worker_cycle_time_s
        cls.worker_name = worker_name

        # register
        WORKERS.append(cls)
        return cls

    # if no args were passed, _cls is the class itself
    if _cls is None:
        return decorator
    else:
        return decorator(_cls)

def load_all_workers():
    """
    Dynamically import every .py in this package so that
    @register_worker decorators run and populate WORKERS.
    """
    package_name = __name__  # here it's 'workers.loader'; we'll tweak below
    package_path = Path(__file__).parent

    # We want the package root, so strip off '.loader'
    root = package_name.rsplit(".", 1)[0]

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        importlib.import_module(f"{root}.{module_name}")