from error_assistant.error_assistant_config.config import Config
import os


config: Config = Config()


def edit_config():
    print("Opening the config file for editing...")
    os.system(f"nano {config.CONFIG_PATH}")