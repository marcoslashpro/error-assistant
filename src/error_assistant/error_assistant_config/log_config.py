import logging
from error_assistant.error_assistant_config.config import Config


config: Config = Config()


def create_logger(name: str):
    logger = logging.getLogger(name)
    class VectorHandler(logging.Handler):
        def emit(self, log):
            from error_assistant.error_agent.agent import code_agent
            from error_assistant.error_agent.prompts import error_agent_prompt

            log_entry = {
                "timestamp": log.asctime,
                "module": log.filename,
                "line": log.lineno,
                "message": log.getMessage()
            }

            code_agent({'role': 'user', 'content': f'{error_agent_prompt}{log_entry}'})

    AGENT_LEVEL_NUM = 55
    AGENT_LEVEL_NAME = "AGENT"

    logging.addLevelName(AGENT_LEVEL_NUM, AGENT_LEVEL_NAME)

    def agent(self, message, *args, **kwargs):
        """
        Log 'message % args' with severity 'AGENT'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.agent("Houston, we have an %s", "flag", exc_info=1)
        """
        if self.isEnabledFor(AGENT_LEVEL_NUM):
            self._log(AGENT_LEVEL_NUM, message, args, **kwargs, stacklevel=2)

    logging.Logger.agent = agent

    base_path = config.config['paths']['code_base_path']
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - Message level: %(levelname)s - Module: %(module)s - Line: %(lineno)d - Message: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

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
    vectorHandler.setLevel(AGENT_LEVEL_NUM)
    vectorHandler.setFormatter(formatter)
    logger.addHandler(vectorHandler)

    return logger
