from error_assistant.error_agent.agent import code_agent
from error_assistant.error_assistant_config.config import Config


config: Config = Config()


def debug():
    try:
        with open(config.config['paths']['log_file_path'], 'r') as f:
            log: str = f.readlines()[-1]

    except FileNotFoundError:
        print(f'Logs file not found, please set it up using \'error_assistant.error_assistant_config.log_config\'')
        raise

    except IndexError:
        print(f'Log file is empty at the moment.')
        raise


        if log:
            code_agent({'role': 'user', 'content': f'Help me debug: log_error_message= {log}'})
        else:
            print("Please provide a log error message to debug.")