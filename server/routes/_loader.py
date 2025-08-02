import importlib
import pkgutil
from pathlib import Path

BLUEPRINTS = []

def register_route(build_fn):
    """
    Decorator for a *function* that returns a Blueprint.
    The returned blueprint is added to BLUEPRINTS.
    """
    bp = build_fn() # execute the builder
    BLUEPRINTS.append(bp)
    return build_fn

def load_all_blueprints():
    """
    Dynamically import every .py in this package so that
    @register_route decorators run and populate BLUEPRINTS.
    """
    package_name = __name__
    package_path = Path(__file__).parent

    # We want the package root, so strip off '.loader'
    root = package_name.rsplit(".", 1)[0]

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        importlib.import_module(f"{root}.{module_name}")