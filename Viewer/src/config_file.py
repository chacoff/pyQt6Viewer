import json


class ConfigLoader:
    def __init__(self):
        super().__init__()
        self.config_path: str = 'src/config.json'
        self.config: any = None
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

    def get_folder(self):
        return self.config.get('folder', '.\\dev')

    def get_model(self):
        return self.config.get('model', '.\\best')
