import os
import json

class Config:
    def __init__(self,
                 config_filepath: str = ''):

        self.config_filepath = 'configuration.json' if not config_filepath else config_filepath
        self._load_config()

    def _load_config(self):
        # load the configuration json file
        with open(self.config_filepath, 'r') as f_in:
            self.config = json.load(f_in)

    def get(self,
            reload: bool = False):

        if reload:
            self._load_config()

        return self.config

class WorkerBootstrap:
    def __init__(self,
                 config_filepath: str = ''):
        # mark as not working by default
        self.working = False

        self.config = Config(config_filepath=config_filepath)

    def _should_exit(self):
        possible_exit_filepaths = ['exit',
                                   os.path.join('.', 'exit')]
        return any([os.path.isfile(_) for _ in possible_exit_filepaths])

    def work(self) -> int:
        pass