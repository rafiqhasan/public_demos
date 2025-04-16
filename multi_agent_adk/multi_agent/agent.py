# import langgraph
# import langchain
import requests

# from langchain_google_vertexai import ChatVertexAI
from typing import TypedDict, Annotated, Literal, List, Dict, Any, Optional
# from typing_extensions import Annotated
from google.cloud import aiplatform
from google.adk.agents import LlmAgent

PROJECT_ID = "hasanrafiq-test-331814"  # @param {type:"string"}
VERTEX_LOCATION = "us-central1"  # @param {type:"string"}

API_KEY = "AIzaSyDIK9C8dOorSDI6bpq2pPtQqgkS7K9qM7Q" # @param {type:"string"}
CX = "a626e35257e324d04" # @param {type:"string"}

def google_search(query: str) -> List[Dict[str, Any]]:
    """
    This tool can be used to search on Google directly to get
    get real time information. This can only take one query at a time and for multiple
    queries, you will have to call this function multiple times.

    Parameters:
    - query (str): The search query

    Returns:
    - List[Dict[str, Any]]: A list of search result dictionaries
    """
    base_url = "https://www.googleapis.com/customsearch/v1"

    # Required parameters
    params = {
        'q': query,
        'key': API_KEY,
        'cx': CX
    }

    try:
        print(f"Querying Google: {query}")

        # Make the request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        results = response.json()

        # Extract and clean up the results
        if 'items' in results:
            search_results = []

            for item in results['items']:
                result_dict = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', '')
                }

                # Add image information if available
                if 'pagemap' in item and 'cse_image' in item['pagemap']:
                    result_dict['image_url'] = item['pagemap']['cse_image'][0].get('src', '')

                search_results.append(result_dict)

            return search_results
        else:
            # Return empty list if no results
            return []

    except Exception as e:
        # Handle exceptions - for LangGraph tools, it's often better to return empty results
        # than to raise exceptions that could break the flow
        print(f"Error performing search: {e}")
        return []

def flight_booking_tool(from_location: str, to_location: str, passenger_name: str, date: str):
    #Dummy
    return {'flight_id': '123456', 'passenger_name': passenger_name, 'from': from_location, 'to': to_location}

search_agent = LlmAgent(name="Google_Search",
                        description="Performs a Google search",
                        tools=[google_search])

flight_agent = LlmAgent(name="Flight_Booking",
                        description="Handles requests to Book flights tickets",
                        tools=[flight_booking_tool])

root_agent = LlmAgent(
    name="RequestCoordinator",
    model="gemini-2.0-flash",
    instruction="Route user requests: Use Google Search agent for performing search, Flight Booking for booking flight tickets.",
    description="Main help desk router.",
    sub_agents=[search_agent, flight_agent]
)
