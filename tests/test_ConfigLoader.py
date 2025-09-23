import unittest
from pyfakefs.fake_filesystem_unittest import Patcher


class TestConfigLoader(unittest.TestCase):
    def test_config_loader_raises_error_if_file_not_found(self):
        with Patcher():
            with self.assertRaises(ConfigNotFoundError):
                loader = ConfigLoader(config_name="config.yaml")
                loader.load_config()

    def test_config_loader_raises_error_on_invalid_yaml(self):
        invalid_yaml = """
plugins:
  - name: "test"
    - key: "value" 
"""
        with Patcher() as patcher:
            loader = ConfigLoader(config_name="config.yaml")
            patcher.fs.create_file(loader.config_path, contents=invalid_yaml)
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
            loader = ConfigLoader(config_name="config.yaml")
            patcher.fs.create_file(loader.config_path, contents=test_yaml)
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
            loader = ConfigLoader(config_name="config.yaml")
            patcher.fs.create_file(loader.config_path, contents=test_yaml)
            actual_result = loader.load_config()
            self.assertIsInstance(actual_result, dict)
            self.assertEqual(expected_results, actual_result)
