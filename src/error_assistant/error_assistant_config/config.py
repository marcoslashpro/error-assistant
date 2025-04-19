import tomllib
import os
from pathlib import Path
import error_assistant.error_assistant_config


class Config:
    def __init__(self) -> None:
        # Dynamically resolve path relative to this file
        package_path = os.path.dirname(error_assistant.error_assistant_config.__file__)
        self.CONFIG_PATH = Path(package_path) / "config.toml"

        # Load the configuration
        with open(self.CONFIG_PATH, 'rb') as f:
            self.config = tomllib.load(f)

    def get(self, section: str, key: str, default: str | None = None):
        return self.config.get(section, {}).get(key, default)
