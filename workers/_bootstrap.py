import os
import json

class Config:
    def __init__(self,
                 config_filepath: str = ''):

        self.config_filepath = 'configuration.json' if not config_filepath else config_filepath
        self._load_config()

    @staticmethod
    def deep_merge(base_dict, new_dict):
        """Recursively merge new_dict into base_dict"""
        for key, value in new_dict.items():
            if (key in base_dict and
                    isinstance(base_dict[key], dict) and
                    isinstance(value, dict)):
                deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict

    def _load_config(self):
        # load the configuration json file
        with open(self.config_filepath, 'r') as f_in:
            self.config = json.load(f_in)

    def get(self,
            reload: bool = False):

        if reload:
            self._load_config()

        return self.config

    def save_config(self,
                    new_config_changes: dict = {}):
        if new_config_changes:
            self.config = Config.deep_merge(self.config, new_config_changes)
            try:
                with open(self.config_filepath, 'w') as f_out:
                    json.dump(self.config, f_out)
                return True
            except:
                return False

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