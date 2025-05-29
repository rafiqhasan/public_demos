# agent.py
from google.adk.agents.llm_agent import LlmAgent, Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

def create_agent():
  """Gets tools from MCP Server."""

  search_agent = LlmAgent(name="Google_Search",
                        description="Performs a Google search",
                        tools=[MCPToolset(
                                connection_params=SseServerParams(
                                    url="http://0.0.0.0:8000/sse",
                                )
                            )])

  flight_agent = LlmAgent(name="Flight_Booking",
                          description="Handles requests to Book flights tickets",
                          tools=[MCPToolset(
                                connection_params=SseServerParams(
                                    url="http://0.0.0.0:8001/sse",
                                )
                            )])

  root_agent = LlmAgent(
      name="RequestCoordinator",
      model="gemini-2.0-flash",
      instruction="Route user requests: Use Google Search agent for performing search, Flight Booking for booking flight tickets.",
      description="Main help desk router.",
      sub_agents=[search_agent, flight_agent]
  )
  return root_agent

root_agent = create_agent()