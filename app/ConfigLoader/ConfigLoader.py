from pathlib import Path

import yaml

from app.exceptions import ConfigNotFoundError, InvalidYamlError, YamlMissingKeyError

class ConfigLoader:
    """
    Handles loading and validation of YAML config files.

    This class is used to load user defined config files in YAML format. It loads
    and validates that config files are valid and contain required sections.

    Attributes:
        config_path (dict): Path to config YAML file. Defaults to project root
    """
    def __init__(self, config_name = "config.yaml"):
        """
        Initializes ConfigLoader object and check that defined config file exists in 
        project root directory.

        Args:
            config_name (str): name of config file. Defaults to config.yaml

        Raises:
            ConfigNotFoundError: If config file is not found
        """
        project_root = Path(__file__).resolve().parent.parent.parent
        self.config_path = project_root / config_name
        if not self.config_path.is_file():
            raise ConfigNotFoundError("Unable to find config file")

    def load_config(self):
        """
        Reads config file, validates all required section exist and converts to dict

        Returns:
            data (dict): config file converted to dict

        Raises:
            InvalidYamlError: If yaml is invalid for any reason
            YamlMissingKeyError: If yaml is mssing required section keys.
        """
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
