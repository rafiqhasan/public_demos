from typing import TypedDict, Annotated, Literal, List, Dict, Any
import httpx
from mcp.server.fastmcp import FastMCP
import asyncio
import requests
import random
import string
from datetime import datetime, timedelta

# Use a relative import that works in both contexts
try:
    # When imported as a module from ADK
    from multi_agent.constants import PROJECT_ID, LOCATION, STAGING_BUCKET, API_KEY, CX, AMADEUS_API_KEY, AMADEUS_API_SECRET
except ModuleNotFoundError:
    # When run directly or imported from current directory
    from constants import PROJECT_ID, LOCATION, STAGING_BUCKET, API_KEY, CX, AMADEUS_API_KEY, AMADEUS_API_SECRET

# Initialize FastMCP server
mcp = FastMCP("travel-booking-server", port=8001)

def generate_booking_reference():
    """Generate a random booking reference"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def calculate_nights(checkin: str, checkout: str):
    """Calculate number of nights between dates"""
    try:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        return (checkout_date - checkin_date).days
    except:
        return 1  # Default to 1 night if date parsing fails

async def get_amadeus_access_token():
    """Get access token for Amadeus API"""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Failed to get Amadeus token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting Amadeus token: {e}")
        return None

async def get_city_code(city_name: str, access_token: str):
    """Get IATA city code using Amadeus City Search API"""
    url = "https://test.api.amadeus.com/v1/reference-data/locations/cities"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {
        "keyword": city_name.upper(),  # API expects uppercase
        "max": 1,
        "include": ["AIRPORTS"]  # Include airports in response
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                city_data = data['data'][0]
                return city_data.get('iataCode')
        else:
            print(f"City search failed: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error getting city code: {e}")
        return None

@mcp.tool()
async def search_hotels(location: str, checkin_date: str, checkout_date: str, guests: int = 2, max_price: int = None) -> List[Dict[str, Any]]:
    """
    Search for available hotels using various filters, this is important before booking hotels
    
    Parameters:
    - location (str): City name (e.g., "Warsaw", "Krakow", "Berlin")
    - checkin_date (str): Check-in date in YYYY-MM-DD format
    - checkout_date (str): Check-out date in YYYY-MM-DD format
    - guests (int): Number of guests (default: 2)
    - max_price (int, optional): Maximum price per night filter
    
    Returns:
    - List[Dict]: Available hotels with details from Amadeus
    """
    print(f"Searching hotels via Amadeus API in {location} from {checkin_date} to {checkout_date} for {guests} guests")
    
    try:
        # Get access token
        access_token = await get_amadeus_access_token()
        if not access_token:
            return [{'error': 'Unable to authenticate with Amadeus API'}]
        
        # Get city code first
        city_code = await get_city_code(location, access_token)
        if not city_code:
            return [{'error': f'Unable to find city code for {location}. Please try cities like PAR, WAW, BER, etc.'}]
        
        print(f"Found city code: {city_code} for {location}")
        
        # Step 1: Get hotels in the city using Hotel List API
        hotel_list_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        params = {
            "cityCode": city_code,
            "radius": 15,  # 15km radius
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
        
        response = requests.get(hotel_list_url, headers=headers, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"Hotel list API failed with status {response.status_code}: {response.text}")
            return [{'error': f'Hotel search failed (Status: {response.status_code})'}]
        
        data = response.json()
        
        if not data.get('data'):
            return [{'message': f'No hotels found in {location} ({city_code})'}]
        
        # Step 2: For demo purposes, we'll add mock pricing to the real hotel data
        # In production, you'd call the Hotel Shopping API for each hotel
        hotels = []
        nights = calculate_nights(checkin_date, checkout_date)
        
        for hotel_data in data['data'][:10]:  # Limit to top 10 results
            # Generate realistic mock pricing based on hotel data
            base_price = random.randint(80, 350)
            if max_price and base_price > max_price:
                continue
                
            hotel_info = {
                'id': hotel_data.get('hotelId', ''),
                'name': hotel_data.get('name', 'Unknown Hotel'),
                'chain_code': hotel_data.get('chainCode', ''),
                'city_code': hotel_data.get('iataCode', city_code),
                'address': hotel_data.get('address', {}).get('countryCode', ''),
                'coordinates': {
                    'latitude': hotel_data.get('geoCode', {}).get('latitude', 0),
                    'longitude': hotel_data.get('geoCode', {}).get('longitude', 0)
                },
                'distance_to_center': hotel_data.get('distance', {}).get('value', 0),
                'distance_unit': hotel_data.get('distance', {}).get('unit', 'KM'),
                
                # Mock pricing data (in production, get from Hotel Shopping API)
                'price_per_night': base_price,
                'total_price': base_price * nights,
                'currency': 'EUR',
                'rating': random.choice([3.5, 4.0, 4.2, 4.5, 4.7, 4.8]),
                
                # Booking details
                'checkin_date': checkin_date,
                'checkout_date': checkout_date,
                'guests': guests,
                'nights': nights,
                'room_type': 'Standard Double Room',
                'amenities': random.sample([
                    'WIFI', 'RESTAURANT', 'FITNESS_CENTER', 'SPA', 
                    'PARKING', 'BAR', 'ROOM_SERVICE', 'AIR_CONDITIONING'
                ], k=random.randint(3, 6)),
                'source': 'Amadeus Hotel List API',
                'booking_available': True
            }
            hotels.append(hotel_info)
        
        # Sort by rating (highest first)
        hotels.sort(key=lambda x: x['rating'], reverse=True)
        
        print(f"Found {len(hotels)} hotels in {location}")
        return hotels
        
    except Exception as e:
        print(f"Error calling Amadeus API: {e}")
        return [{'error': f'Hotel search failed: {str(e)}'}]

@mcp.tool()
async def book_hotel(hotel_id: str, guest_name: str, checkin_date: str, checkout_date: str, guests: int = 2, email: str = "guest@example.com") -> Dict[str, Any]:
    """
    Book a hotel room (dummy booking - returns confirmation without real booking).
    
    Parameters:
    - hotel_id (str): Hotel ID from search results
    - guest_name (str): Primary guest name
    - checkin_date (str): Check-in date in YYYY-MM-DD format  
    - checkout_date (str): Check-out date in YYYY-MM-DD format
    - guests (int): Number of guests
    - email (str): Guest email address
    
    Returns:
    - Dict: Booking confirmation details
    """
    print(f"Booking hotel {hotel_id} for {guest_name}")
    
    # Generate booking confirmation
    booking_reference = generate_booking_reference()
    nights = calculate_nights(checkin_date, checkout_date)
    
    # Generate realistic mock pricing
    base_price = random.randint(80, 300)
    total_cost = base_price * nights
    
    # Generate mock hotel name based on hotel_id
    hotel_names = [
        "Grand Hotel Warsaw", "Luxury Palace Hotel", "City Center Hotel", 
        "Business Hotel Premium", "Historic Hotel", "Modern Boutique Hotel"
    ]
    mock_hotel_name = random.choice(hotel_names)
    
    return {
        'success': True,
        'booking_reference': booking_reference,
        'hotel_details': {
            'hotel_id': hotel_id,
            'name': mock_hotel_name,
            'address': f"Mock Address for {hotel_id}",
            'rating': round(random.uniform(4.0, 4.9), 1)
        },
        'booking_details': {
            'guest_name': guest_name,
            'email': email,
            'checkin_date': checkin_date,
            'checkout_date': checkout_date,
            'guests': guests,
            'nights': nights,
            'room_type': 'Standard Double Room',
            'price_per_night': base_price,
            'total_cost': total_cost,
            'currency': 'EUR'
        },
        'confirmation_message': f'Hotel booking confirmed! Reference: {booking_reference}',
        'cancellation_policy': 'Free cancellation up to 24 hours before check-in',
        'payment_status': 'Confirmed',
        'booking_date': '2025-06-06'
    }

@mcp.tool()
async def flight_booking_tool(from_location: str, to_location: str, passenger_name: str, departure_date: str, return_date: str = None) -> Dict[str, Any]:
    """
    Book a flight (dummy booking - returns confirmation without real booking).
    
    Parameters:
    - from_location (str): Departure city
    - to_location (str): Destination city  
    - passenger_name (str): Passenger name
    - departure_date (str): Departure date in YYYY-MM-DD format
    - return_date (str, optional): Return date for round trip
    
    Returns:
    - Dict: Flight booking confirmation
    """
    print(f"Booking flight from {from_location} to {to_location} for {passenger_name}")
    
    flight_reference = generate_booking_reference()
    
    # Mock flight prices and times
    base_price = random.randint(150, 800)
    departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
    
    booking_data = {
        'success': True,
        'flight_reference': flight_reference,
        'passenger_name': passenger_name,
        'outbound_flight': {
            'from': from_location,
            'to': to_location,
            'date': departure_date,
            'time': departure_time,
            'flight_number': f'LO{random.randint(100, 999)}',
            'airline': 'LOT Polish Airlines',
            'price': base_price
        },
        'total_cost': base_price,
        'currency': 'EUR',
        'booking_status': 'Confirmed',
        'confirmation_message': f'Flight booking confirmed! Reference: {flight_reference}'
    }
    
    # Add return flight if requested
    if return_date:
        return_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        booking_data['return_flight'] = {
            'from': to_location,
            'to': from_location,
            'date': return_date,
            'time': return_time,
            'flight_number': f'LO{random.randint(100, 999)}',
            'airline': 'LOT Polish Airlines',
            'price': base_price
        }
        booking_data['total_cost'] = base_price * 2
        booking_data['trip_type'] = 'Round trip'
    else:
        booking_data['trip_type'] = 'One way'
    
    return booking_data

if __name__ == "__main__":
    # Initialize and run the server
    asyncio.run(mcp.run(transport="sse"))