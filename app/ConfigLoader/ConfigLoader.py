from pathlib import Path

import yaml

from app.exceptions import ConfigNotFoundError, InvalidYamlError, YamlMissingKeyError

class ConfigLoader:
    def __init__(self, config_name = "config.yaml"):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.config_path = project_root / config_name
        if not self.config_path.is_file():
            raise ConfigNotFoundError("Unable to find config file")

    def load_config(self):
        required_keys = ["plugins", "severity_levels"]
        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise InvalidYamlError("YAML is not a dict")
            
            missing_keys = required_keys - data.keys()
            if missing_keys:
                raise YamlMissingKeyError(f"YAML is missing the following keys:{' '.join(missing_keys)}", key=" ".join(missing_keys))

            else:
                return data

        except yaml.YAMLError as e:
            raise InvalidYamlError(f"Error parsing YAML file") from e
