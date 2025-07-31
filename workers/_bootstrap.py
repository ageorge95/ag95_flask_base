import os
import json

class WorkerBootstrap:
    def __init__(self):
        # mark as not working by default
        self.working = False

        # load the configuration json file
        self.config = {}
        possible_config_filepaths = ['configuration.json',
                                     os.path.join('.', 'configuration.json')]
        for config_filepath in possible_config_filepaths:
            if os.path.isfile(config_filepath):
                with open('configuration.json', 'r') as f:
                    self.config = json.load(f)
        if not self.config:
            raise Exception('Configuration file not found.')

    def is_working(self):
        return self.working

    def set_working(self):
        self.working = True

    def clear_working(self):
        self.working = False

    def _should_exit(self):
        possible_exit_filepaths = ['exit',
                                   os.path.join('.', 'exit')]
        return any([os.path.isfile(_) for _ in possible_exit_filepaths])

    def work(self) -> int:
        pass