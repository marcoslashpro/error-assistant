from smolagents import HfApiModel, CodeAgent
from smolagents import DuckDuckGoSearchTool

from error_assistant.vector_store.Retriever import Retriever


DuckDuckGoSearchTool.description = """
Searches the web (via DuckDuckGo) for external documentation or third-party code references.

Use this tool to:

Understand unfamiliar APIs, libraries, or external behavior not present in the codebase.

Retrieve best practices or patterns related to the error."""


code_agent: CodeAgent = CodeAgent(
		model=HfApiModel(),
		tools=[Retriever()],
		add_base_tools=True
	)
