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
        cls.worker_module = cls.__module__

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
    Dynamically import every .py in this package and all subpackages recursively.
    @register_worker decorators run and populate WORKERS.
    """
    package_name = __name__.rsplit(".", 1)[0]  # root package
    package_path = Path(__file__).parent

    def import_recursive(current_path, current_package):
        for _, name, is_pkg in pkgutil.iter_modules([str(current_path)]):
            full_name = f"{current_package}.{name}"

            if is_pkg:
                # Recursively import subpackage
                subpackage_path = current_path / name
                import_recursive(subpackage_path, full_name)
            else:
                # Import module
                importlib.import_module(full_name)

    import_recursive(package_path, package_name)