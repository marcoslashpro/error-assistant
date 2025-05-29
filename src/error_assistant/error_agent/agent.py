from smolagents import InferenceClientModel, CodeAgent
from smolagents import DuckDuckGoSearchTool
import os

from error_assistant.vector_store.Retriever import Retriever


hf_token = os.environ.get('HF_TOKEN')
if not hf_token:
	print(f"Please provide an HF_TOKEN environment variable in order to use the CodeAgent")

DuckDuckGoSearchTool.description = """
Searches the web (via DuckDuckGo) for external documentation or third-party code references.

Use this tool to:

Understand unfamiliar APIs, libraries, or external behavior not present in the codebase.

Retrieve best practices or patterns related to the error."""


code_agent: CodeAgent = CodeAgent(
		model=InferenceClientModel(),
		tools=[Retriever()],
		add_base_tools=True
	)
