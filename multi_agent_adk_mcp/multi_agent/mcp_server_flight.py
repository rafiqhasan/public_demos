from typing import TypedDict, Annotated, Literal, List, Dict, Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import asyncio
import requests

# Use a relative import that works in both contexts
try:
    # When imported as a module from ADK
    from multi_agent.constants import PROJECT_ID, LOCATION, STAGING_BUCKET, API_KEY, CX
except ModuleNotFoundError:
    # When run directly or imported from current directory
    from constants import PROJECT_ID, LOCATION, STAGING_BUCKET, API_KEY, CX

# Initialize FastMCP server
mcp = FastMCP("flight-booking-server", port=8001)

@mcp.tool()
async def flight_booking_tool(from_location: str, to_location: str, passenger_name: str, date: str):
    #Dummy
    return {'flight_id': '123456', 'passenger_name': passenger_name, 'from': from_location, 'to': to_location}

if __name__ == "__main__":
    # Initialize and run the server
    asyncio.run(mcp.run(transport="sse"))
