import tomllib
import os
from pathlib import Path

class Config:
    def __init__(self) -> None:
        # Dynamically resolve path relative to this file
        self.CONFIG_PATH = Path(__file__).parent / "config.toml"

        # If the file doesn't exist, create it with boilerplate content
        if not self.CONFIG_PATH.exists():
            self.create_boilerplate_config()

        # Load the configuration
        with open(self.CONFIG_PATH, 'rb') as f:
            self.config = tomllib.load(f)

    def create_boilerplate_config(self):
        boilerplate = """
[paths]
code_base_path = '.'

[paths.ignores]
directories = ['env', '__pycache__', '.git', '.gitignore', '.mypy_cache', '.pytest_cache']
files = ['.log', '.pyc']

[pinecone]
api_key = your-api-key
"code-index_name" = 'error-assistant-index'  

[pinecone.code-namespace]
name = 'code-namespace'
top-k = 10

[agent]
hf-token = 'your_hf_token'
"""
        with open(self.CONFIG_PATH, 'w') as f:
            f.write(boilerplate.strip())
        
        print(f"\n🚨 Config file created at {self.CONFIG_PATH}")
        print("🔧 Please edit this file with your personal details before continuing.\n")
        exit(1)  # Stop execution until the config is completed

    def get(self, section: str, key: str, default: str | None = None):
        return self.config.get(section, {}).get(key, default)
