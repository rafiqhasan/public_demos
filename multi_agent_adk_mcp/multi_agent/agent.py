# agent.py
from contextlib import AsyncExitStack
from google.adk.agents.llm_agent import LlmAgent, Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

async def create_agent():
  """Gets tools from MCP Server."""
  common_exit_stack = AsyncExitStack()

  # Get MCP Tools - Google Search Server 
  search_tools, _ = await MCPToolset.from_server(
      connection_params=SseServerParams(
          url="http://0.0.0.0:8000/sse",
      ),
      async_exit_stack=common_exit_stack
  )

  # Get MCP Tools - Flight booking Server
  flight_tools, _ = await MCPToolset.from_server(
      connection_params=SseServerParams(
          url="http://0.0.0.0:8001/sse",
      ),
      async_exit_stack=common_exit_stack
  )

  search_agent = LlmAgent(name="Google_Search",
                        description="Performs a Google search",
                        tools=[*search_tools])

  flight_agent = LlmAgent(name="Flight_Booking",
                          description="Handles requests to Book flights tickets",
                          tools=[*flight_tools])

  root_agent = LlmAgent(
      name="RequestCoordinator",
      model="gemini-2.0-flash",
      instruction="Route user requests: Use Google Search agent for performing search, Flight Booking for booking flight tickets.",
      description="Main help desk router.",
      sub_agents=[search_agent, flight_agent]
  )
  return root_agent, common_exit_stack

root_agent = create_agent()