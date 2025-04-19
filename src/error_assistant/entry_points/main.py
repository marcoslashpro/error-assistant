#!/usr/bin/env python3

import logging
import os
import threading
from argparse import ArgumentParser

from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import log_config
from error_assistant.vector_store.Retriever import Retriever
from error_assistant.vectorizer.Vectorizer import Vectorizer
from error_assistant.error_agent.agent import code_agent
from error_assistant.watchers.Observer import CodeWatcher
from error_assistant.watchers.CodeBaseHandler import CodeBaseHandler
from error_assistant.entry_points import chat, debug, edit

from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff


# Load config
config: Config = Config()

#Coonfig the logger
logger = logging.getLogger(__name__)
log_config(logger)


def main():
    
    try:
        print('Connecting...')
        retriever: Retriever = Retriever()
        code_watcher: CodeWatcher = CodeWatcher(CodeBaseHandler)
        code_watcher.setup()
        print('Connected! \n')

        print("\nWelcome to the Error Assistant CLI!")
        print("Perform various actions like searching code, debugging errors, or updating the vector store.\n")


        while True:
            user_input: str = input('> ').strip()

            if 'edit config' in user_input or '-ec' in user_input:
                edit.edit_config()

            elif 'chat' in user_input or '-c' in user_input:
                chat.chat()

            elif 'update' in user_input or '-u' in user_input:
                latest_snapshot: DirectorySnapshot = code_watcher.take_snapshot()
                snap_diff: DirectorySnapshotDiff = DirectorySnapshotDiff(latest_snapshot, code_watcher.new_snapshot)

                if snap_diff: code_watcher.update_vectorStore(snap_diff)

            else:
                print('Invalid command, type \'-h\' for help.')

    except KeyboardInterrupt:
        code_watcher.close()


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
