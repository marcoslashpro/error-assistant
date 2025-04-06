import tomllib
import os
from pathlib import Path


class Config:
    def __init__(self) -> None:
        # Dynamically resolve path relative to this file
        self.CONFIG_PATH = Path(__file__).parent / "config.toml"

        # Load the configuration
        with open(self.CONFIG_PATH, 'rb') as f:
            self.config = tomllib.load(f)


    def get(self, section: str, key: str, default: str | None = None):
        return self.config.get(section, {}).get(key, default)