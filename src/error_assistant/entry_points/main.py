#!/usr/bin/env python3

import logging

from argparse import ArgumentParser

from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import create_logger

from error_assistant.watchers.Observer import CodeWatcher
from error_assistant.watchers.CodeBaseHandler import CodeBaseHandler
from error_assistant.entry_points import chat, debug, edit

from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff


# Load config
config: Config = Config()

#Config the logger
logger = create_logger(__name__)


def main():
    try:
        print('Connecting...')
        code_watcher: CodeWatcher = CodeWatcher(CodeBaseHandler)
        code_watcher.setup()
        print('Connected! \n')
        print('Observing: -.-')
        while True:
            user_input: str = input('> ').strip()

            if 'edit config' in user_input or '-ec' in user_input:
                edit.edit_config()

            elif 'chat' in user_input or '-c' in user_input:
                chat.chat()

            elif 'debug' in user_input or '-d' in user_input:
                try:
                    debug.debug()
                except RuntimeError as e:
                    print(e)

            elif 'update' in user_input or '-u' in user_input:
                latest_snapshot: DirectorySnapshot = code_watcher.take_snapshot()
                snap_diff: DirectorySnapshotDiff = DirectorySnapshotDiff(latest_snapshot, code_watcher.new_snapshot)

                if snap_diff: code_watcher.update_vector_store(snap_diff)

            elif '-h' in user_input or 'help' in user_input:
                print(f'List of commands: \n'
                      'debug or -d: Runs inference on the model on the last logged error in the log file'
                      ' provided in the config file\n'
                      'chat or -c: Prompts you for a question to run to the model.\n'
                      'edit config or -ec: Opens the config file in the nano editor to allow modifications')

            else:
                print('Invalid command, type \'-h\' for help, ctrl+c to quit')

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
        edit.edit_config()
    else:
        main()
