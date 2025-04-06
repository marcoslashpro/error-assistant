#!/usr/bin/env python3

import logging
import os
import threading
from argparse import ArgumentParser

from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import log_config
from error_assistant.watchers.code_base_observer import CodeBaseHandler
from watchdog.observers import Observer
from error_assistant.error_agent.agent import code_agent
from error_assistant.vector_store.Retriever import Retriever
from error_assistant.vectorizer.Vectorizer import Vectorizer


# Load config
config: Config = Config()

#Coonfig the logger
logger = logging.getLogger(__name__)
log_config(logger)


# Start the observer in a separate thread
def start_observer():
    observer = Observer()
    event_handler = CodeBaseHandler(Vectorizer())
    observer.schedule(event_handler, path=config.config['paths']['code_base_path'], recursive=True)  # Adjust path if needed
    observer.start()
    return observer


def edit_config():
    print("Opening the config file for editing...")
    os.system(f"nano {config.CONFIG_PATH}")  # Or use another text editor


def main():
    print("\nWelcome to the Error Assistant CLI!")
    print("Perform various actions like searching code, debugging errors, or updating the vector store.\n")
    
    try:
        observer = start_observer()

        while True:
            user_input: str = input('> ').strip()

            if 'search code' in user_input or '-sc' in user_input:
                search_input: str = input(':search code> ').strip()
                if search_input:
                    print(Retriever().forward(search_input))
                else:
                    print("Please provide a search term for the code base.")
                
                
            elif 'debug' in user_input or '-d' in user_input:
                debug_input: str = input(':debug> ').strip()
                if debug_input:
                    code_agent({'role': 'user', 'content': f'Help me debug: log_error_message= {debug_input}'})
                else:
                    print("Please provide a log error message to debug.")

            elif 'update_code' in user_input or '-uc' in user_input:
                print("Updating code base... This might take a few moments.")
                print(Vectorizer().prepare_code_records())
                print('Code base updated successfully!')

            elif 'config edit' in user_input or '-ce' in user_input:
                edit_config()

            elif 'help' in user_input or '-h' in user_input:
                print("""
Available commands:
  - search code  (-sc)  : Search for a string in the code base.
  - search logs  (-sl)  : Search for a string in the log base.
  - debug        (-d)   : Provide a log error message and get debugging advice.
  - update_code  (-uc)  : Re-analyze the code base and update the vector store.
  - config edit  (-ce)  : Open config.toml for modification.
  - help         (-h)   : Display this help message.
                """)

            else:
                print('Invalid command, type \'-h\' for help.')

    except KeyboardInterrupt:
        print("\nExiting the program.")
        observer.stop()
        observer.join()  # Wait for the observer thread to finish

if __name__ == '__main__':
    parser = ArgumentParser(description="Error Assistant CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Config edit command
    config_parser = subparsers.add_parser("config", help="Modify configuration")
    config_parser.add_argument("action", choices=["edit"], help="Edit the config file")

    args = parser.parse_args()

    if args.command == "config" and args.action == "edit":
        edit_config()
    else:
        main()
