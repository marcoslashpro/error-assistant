from smolagents import HfApiModel, CodeAgent
from smolagents import DuckDuckGoSearchTool

from error_assistant.vector_store.Retriever import Retriever


DuckDuckGoSearchTool.description = '''Performs a duckduckgo web search based on your query (think a Google search) then returns the top search results.
This tool should be used to gather information about external information about the code base (think info about APIs).'''


code_agent: CodeAgent = CodeAgent(
		model=HfApiModel(),
		tools=[Retriever()],
		add_base_tools=True
	)