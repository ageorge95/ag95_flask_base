'''
Template prerequisite module.

A prerequisite is a small, one-shot preparation task that runs immediately
before a worker (or service) that references it.  Prerequisites:

  - are NOT registered in the WORKERS list and are NEVER executed in a
    loop or on their own (they only run as part of a worker that declares
    them via register_worker_prerequisite())
  - live in the "workers/" directory alongside workers and services
  - are referenced by NAME, e.g.

        @register_worker(worker_cycle_time_s=60 * 60,
                         worker_name=os.path.basename(__file__).replace('.py', ''))
        @register_worker_prerequisite(['_template_prerequsite'])
        class Worker(WorkerBootstrap):
            ...

  - can be run standalone for development/testing:

        python -m workers._template_prerequsite

Create your own by following this template; any module that is referenced as
a prerequisite only needs to exit with code 0 on success.
'''

import os
import json


def main() -> int:
    """
    Do the preparation work here and return 0 on success (non-zero on failure).
    """
    config_path = 'configuration.json'
    with open(config_path, 'r') as handle:
        config = json.load(handle)

    print(f"Prerequisite ran for: {config.get('framework_title', 'unknown')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
