import unittest
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import Patcher

from app.ConfigLoader import ConfigLoader
from app.exceptions import ConfigNotFoundError, InvalidYamlError, YamlMissingKeyError


class TestConfigLoader(unittest.TestCase):
    def setUp(self, config_name = "config.yaml"):
        project_root = Path(__file__).resolve().parent.parent
        self.config_path = project_root / config_name

    def test_config_loader_raises_error_if_file_not_found(self):
        with Patcher():
            with self.assertRaises(ConfigNotFoundError):
                loader = ConfigLoader(config_name="config.yaml")


    def test_config_loader_raises_error_on_invalid_yaml(self):
        invalid_yaml = """
plugins:
  - name: "test"
    - key: "value" 
"""
        with Patcher() as patcher:
            patcher.fs.create_file(self.config_path, contents=invalid_yaml)
            loader = ConfigLoader(config_name="config.yaml")
            with self.assertRaises(InvalidYamlError):
                loader.load_config()

    def test_config_loader_raises_error_on_missing_key(self):
        test_yaml = """
    plugins:
        - name: "default_email_sender"
          config:
                recipient_email: "user@domain.com"
                smtp_server: "smtp.gmail.com"
                smtp_port: 587
    """
        with Patcher() as patcher:
            patcher.fs.create_file(self.config_path, contents=test_yaml)
            loader = ConfigLoader(config_name="config.yaml")
            with self.assertRaises(YamlMissingKeyError):
                loader.load_config()

    def test_config_returns_config_as_dict(self):
        test_yaml = """
plugins:
  - name: default_email_sender
    type: smtp_sender
    config:
      recipient_email: user@domain.com
      smtp_server: smtp.gmail.com
      smtp_port: 587
severity_levels:
  normal:
    - default_email_sender
  urgent:
    - default_email_sender
  critical:
    - default_email_sender
  mfa:
    - default_email_sender
        """
        expected_results = {
            "plugins": [
                {
                    "name": "default_email_sender",
                    "type": "smtp_sender",
                    "config": {
                        "recipient_email": "user@domain.com",
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587
                    }
                }
            ],
            "severity_levels": {
                    "normal": ["default_email_sender"],
                    "urgent": ["default_email_sender"],
                    "critical": ["default_email_sender"],
                    "mfa": ["default_email_sender"]
            }
        }

        with Patcher() as patcher:
            patcher.fs.create_file(self.config_path, contents=test_yaml)
            loader = ConfigLoader(config_name="config.yaml")
            actual_result = loader.load_config()
            self.assertIsInstance(actual_result, dict)
            self.assertEqual(expected_results, actual_result)
