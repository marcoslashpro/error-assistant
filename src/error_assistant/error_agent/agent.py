from smolagents import InferenceClientModel, CodeAgent
from smolagents import DuckDuckGoSearchTool
from huggingface_hub.errors import HfHubHTTPError

from error_assistant.vector_store.Retriever import Retriever

DuckDuckGoSearchTool.description = """
Searches the web (via DuckDuckGo) for external documentation or third-party code references.

Use this tool to:

Understand unfamiliar APIs, libraries, or external behavior not present in the codebase.

Retrieve best practices or patterns related to the error."""


try:
	code_agent: CodeAgent = CodeAgent(
			model=InferenceClientModel(),
			tools=[Retriever()],
			add_base_tools=True
		)
except HfHubHTTPError as e:
	if e.response is not None and e.response.status_code == 401:
		print('In order to use the code agent, you must provide a valid '
				'HF_TOKEN(With READ permission and permissions to `Make calls to Inference Providers`)' \
				' by doing `huggingface-cli login` and then inserting your token.')
		raise
