from error_assistant.error_agent.agent import code_agent
from argparse import ArgumentParser
import sys


def chat() -> None:
	if len(sys.argv) == 2:
		user_input: str | None = sys.argv[-1]
	else:
		user_input = None

	while True:
		if not user_input:
			user_input: str | None = input('chat> ')
			if user_input == 'quit' or user_input == 'q':
				break

		code_agent({'role': 'user', 'content': user_input})
		break
