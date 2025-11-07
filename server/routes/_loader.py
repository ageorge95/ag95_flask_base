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
                    print(f"✓ Loaded blueprints from: {full_name}")
                except Exception as e:
                    print(f"✗ Failed to import {full_name}: {e}")

    import_recursive(package_path, package_name)