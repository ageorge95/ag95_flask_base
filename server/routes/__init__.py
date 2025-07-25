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

# --- auto-import every .py file in this package -----------------
package_name = __name__
package_path = Path(__file__).parent
for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
    importlib.import_module(f"{package_name}.{module_name}")