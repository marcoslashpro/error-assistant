import logging
from error_assistant.error_assistant_config.config import Config


config: Config = Config()


def log_config(logger):
    class VectorHandler(logging.Handler):
        def emit(self, log):
            from error_agent.agent import code_agent
            from error_agent.prompts import log_prompt
            
            log_entry = {
                "timestamp": log.asctime,
                "level": log.levelname,
                "module": log.module,
                "line": log.lineno,
                "message": log.getMessage()
            }
            code_agent({'role': 'user', 'content': f'{log_prompt}{log_entry}'})
        
    base_path = config.config['paths']['code_base_path']
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - Message level: %(levelname)s - Module: %(module)s - Line: %(lineno)d - Message: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')


    fileHandler = logging.FileHandler(
            filename=f'{base_path}/logs.log',
            encoding='utf-8'
        )
    fileHandler.setLevel(logging.ERROR)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)


    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


    vectorHandler = VectorHandler()
    vectorHandler.setLevel(logging.ERROR)
    logger.addHandler(vectorHandler)