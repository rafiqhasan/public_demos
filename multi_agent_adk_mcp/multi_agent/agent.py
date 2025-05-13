# agent.py
from contextlib import AsyncExitStack
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams

async def create_agent():
  """Gets tools from MCP Server."""
  common_exit_stack = AsyncExitStack()

  remote_tools, _ = await MCPToolset.from_server(
      connection_params=SseServerParams(
          # TODO: IMPORTANT! Change the path below to your remote MCP Server path
          url="http://0.0.0.0:8000/sse",
      ),
      async_exit_stack=common_exit_stack
  )

  agent = LlmAgent(
      model='gemini-2.0-flash',
      name='enterprise_assistant',
      instruction=(
          'Help user in searching through Google'
      ),
      tools=remote_tools
  )
  return agent, common_exit_stack

root_agent = create_agent()