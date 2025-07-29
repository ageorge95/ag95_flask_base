# Expose the loader and the registry; no side-effects:
from .loader import load_all_workers, WORKERS

# will prevent any worker from running
# usually needed when only the server (and its routes) is needed without any worker
DO_NOT_RUN_ANY_WORKER_BOOL = False