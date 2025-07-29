import importlib
import pkgutil
from pathlib import Path

WORKERS = []

def register_worker(_cls=None,
                    *,
                    worker_cycle_time_s,
                    worker_name):
    def decorator(cls):
        # instantiate
        instance = cls()

        # attach metadata
        instance.worker_cycle_time_s = worker_cycle_time_s
        instance.worker_name = worker_name

        # register
        WORKERS.append(instance)
        return cls

    # if no args were passed, _cls is the class itself
    if _cls is None:
        return decorator
    else:
        return decorator(_cls)

# --- auto-import every .py file in this package -----------------
package_name = __name__
package_path = Path(__file__).parent
for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
    importlib.import_module(f"{package_name}.{module_name}")