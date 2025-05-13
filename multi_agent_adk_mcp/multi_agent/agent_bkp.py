############################# v1

import requests

from typing import TypedDict, Annotated, Literal, List, Dict, Any, Optional
from contextlib import AsyncExitStack
from google.cloud import aiplatform
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

async def create_agent():
    """Gets tools from the File System MCP Server."""
    print("Attempting to connect to MCP Filesystem server...")
    common_exit_stack = AsyncExitStack()

    tools, _ = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://0.0.0.0:8000/sse",
        ),
        async_exit_stack=common_exit_stack
    )

    search_agent = LlmAgent(name="Google_Search",
                            description="Performs a Google search",
                            tools=tools)

    root_agent = LlmAgent(
        name="RequestCoordinator",
        model="gemini-2.0-flash",
        instruction="Route user requests: Use Google Search agent for performing search",
        description="Main help desk router.",
        sub_agents=[search_agent]
    )

root_agent = create_agent()

############################# v2

# import requests

# from typing import TypedDict, Annotated, Literal, List, Dict, Any, Optional
# from contextlib import AsyncExitStack
# from google.cloud import aiplatform
# from google.adk.agents import LlmAgent
# from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams

# global root_agent
# root_agent = ""

# async def load_tools():
#     return await MCPToolset.from_server(
#       connection_params=SseServerParams(
#                                 url="http://0.0.0.0:8000/sse",
#                             )
#     )

# # Create a main async function to contain your async operations
# async def main():
#     tools, exit_stack = await load_tools()
#     print("started")
#     print(tools)
#     # Use your tools here
    
#     search_agent = LlmAgent(name="Google_Search",
#                         description="Performs a Google search",
#                         tools=tools)

#     flight_agent = LlmAgent(name="Flight_Booking",
#                         description="Handles requests to Book flights tickets",
#                         tools=tools)

#     root_agent = LlmAgent(
#         name="RequestCoordinator",
#         model="gemini-2.0-flash",
#         instruction="Route user requests: Use Google Search agent for performing search, Flight Booking for booking flight tickets.",
#         description="Main help desk router.",
#         sub_agents=[search_agent, flight_agent]
#     )

#     # Eventually close your exit_stack when done
#     await exit_stack.aclose()  # Uncomment when you're ready to clean up

#     return root_agent

# # Run the async main function
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())


# # common_exit_stack = AsyncExitStack()