import json
import os

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.settings = self.load_config()

        # Resolve relative paths to absolute paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def load_config(self):
        with open(self.config_file, 'r') as file:
            return json.load(file)

    def get_asset_composition(self) -> dict[str, dict[str, any]]:
        return self.settings.get('asset_composition', {})
