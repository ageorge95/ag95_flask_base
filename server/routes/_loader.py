import importlib
import pkgutil
from pathlib import Path
from flask import jsonify
from workers._relay import _detached_execution
from workers import (WORKERS,
                     DO_NOT_RUN_ANY_WORKER_BOOL)

BLUEPRINTS = []

def register_worker_prerequisite(workers):
    """
    Decorator to tag a route build method with worker prerequisites.
    :param workers: A list of strings identifying the workers
     (e.g., [db_sync', 'cache_warmup'])
    """
    def decorator(f):
        # Attach the list to the function object itself
        f._worker_prerequisites = workers
        return f
    return decorator

def register_route(build_fn):
    """
    Decorator for a *function* that returns a Blueprint.
    The returned blueprint is added to BLUEPRINTS.
    """
    # 1. Execute the builder to get the blueprint
    bp = build_fn()

    # 2. Check if the builder has prerequisites attached
    @bp.before_request
    def check_prerequisites():
        required_workers = getattr(build_fn, '_worker_prerequisites', None)
        if required_workers and not DO_NOT_RUN_ANY_WORKER_BOOL:
            for required_worker in required_workers:
                executed = False
                for registered_worker in WORKERS:
                    if registered_worker.worker_name == required_worker:
                        return_code = _detached_execution(registered_worker, True)
                        if return_code != 0:
                            return jsonify({
                                'status': 'error',
                                'message': f'Worker failed to execute.',
                                'required_worker': required_worker,
                                'return_code': return_code
                            }), 503
                        executed = True
                if not executed:
                    return jsonify({
                            'status': 'error',
                            'message': f'Worker not found.',
                            'missing_workers': required_workers,
                            'existing_workers': [_.worker_name for _ in WORKERS]
                        }), 503

    BLUEPRINTS.append(bp)
    return build_fn

def load_all_blueprints():
    """
    Dynamically import every .py in this package and all subpackages recursively.
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
                try:
                    importlib.import_module(full_name)
                    if not name.startswith("_"):
                        print(f"✓ Loaded blueprints from: {full_name}")
                except Exception as e:
                    if not name.startswith("_"):
                        print(f"✗ Failed to import {full_name}: {e}")

    import_recursive(package_path, package_name)