import requests

from typing import TypedDict, Annotated, Literal, List, Dict, Any, Optional
from google.cloud import aiplatform
from google.adk.agents import LlmAgent

from bs4 import BeautifulSoup
from vertexai.preview.generative_models import GenerativeModel
import re

# Use a relative import that works in both contexts
try:
    # When imported as a module from ADK
    from multi_agent.constants import PROJECT_ID, LOCATION, STAGING_BUCKET, API_KEY, CX
except ModuleNotFoundError:
    # When run directly or imported from current directory
    from constants import PROJECT_ID, LOCATION, STAGING_BUCKET, API_KEY, CX

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_recipe(url: str):
    """
    Scrapes a recipe URL using Selenium to handle JavaScript-rendered content.
    
    Args:
        url: The URL of the recipe page to scrape
        
    Returns:
        Dictionary containing the scraped recipe text
    """
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Load the page
        driver.get(url)
        
        # Wait for the page to load and content to be rendered
        # You might need to adjust this based on the specific site
        time.sleep(5)
        
        # Wait for specific elements to load (optional)
        try:
            # Wait for common recipe elements to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            pass  # Continue even if specific elements don't load
        
        # Get the page source after JavaScript execution
        html_content = driver.page_source
        
        # Close the driver
        driver.quit()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        
        # Remove common non-content elements
        for element in soup.find_all(attrs={"class": re.compile(r"(ad|advertisement|sidebar|popup|modal|cookie|consent)", re.I)}):
            element.extract()
        
        # Get all text from the page
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        meaningful_chunks = [chunk for chunk in chunks if chunk and len(chunk) > 2]
        recipe_text = '\n'.join(meaningful_chunks)
        
        # Extract title
        title = None
        if soup.title:
            title = soup.title.get_text().strip()
        
        return {
            'success': True,
            'url': url,
            'title': title,
            'recipe_text': recipe_text,
            'word_count': len(recipe_text.split()),
            'character_count': len(recipe_text)
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Selenium scraping error: {str(e)}'}

def extract_ingredients(recipe_text: str):
    """
    Extracts ingredients from the recipe text using Google's Gemini model via Vertex AI.
    
    Args:
        recipe_text: The full text of a recipe
        
    Returns:
        Dictionary containing a structured list of ingredients with quantities
    """
    try:
        # Initialize the Gemini model
        model = GenerativeModel("gemini-2.0-flash")
        
        # Create a prompt for ingredient extraction
        prompt = f"""
        Extract all ingredients from the following recipe text. 
        For each ingredient, include the quantity, unit (if available), and the ingredient name.
        Format the response as a JSON list of objects with 'quantity', 'unit', and 'name' fields.
        If quantity or unit is not specified, leave the field empty.
        
        RECIPE TEXT:
        {recipe_text}
        
        Response format example:
        [
          {{"quantity": "200", "unit": "g", "name": "spaghetti"}},
          {{"quantity": "2", "unit": "", "name": "eggs"}},
          {{"quantity": "", "unit": "", "name": "salt to taste"}}
        ]
        """
        
        # Generate the response
        response = model.generate_content(prompt)
        
        # Process and parse the response
        try:
            # Try to extract JSON from the response
            # Look for content between ```json and ``` if the model wraps it
            text_content = response.text
            
            # Check if response contains code blocks
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text_content)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no code blocks, try to extract JSON directly
                # Look for arrays that might contain our ingredient list
                json_str = re.search(r'\[\s*{.*}\s*\]', text_content, re.DOTALL)
                if json_str:
                    json_str = json_str.group(0)
                else:
                    json_str = text_content
            
            # Parse the JSON
            ingredients = json.loads(json_str)
            
            return {
                'success': True,
                'ingredients': ingredients
            }
            
        except Exception as json_error:
            # Fallback parsing logic if Gemini doesn't return valid JSON
            # This is a simplified version that extracts text lines that look like ingredients
            lines = response.text.strip().split('\n')
            ingredients = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('```') and not line.endswith('```'):
                    # Try to parse an ingredient line
                    parts = re.match(r'(?:(\d+[\d./]*)?\s*([a-zA-Z]+)?)?\s*(.+)', line)
                    if parts:
                        quantity, unit, name = parts.groups()
                        ingredients.append({
                            "quantity": quantity if quantity else "",
                            "unit": unit if unit else "",
                            "name": name.strip() if name else ""
                        })
            
            return {
                'success': True,
                'ingredients': ingredients,
                'warning': 'Failed to parse as JSON, used fallback parsing'
            }
            
    except Exception as e:
        return {'success': False, 'error': f'Ingredient extraction error: {str(e)}'}

def add_to_basket(user_id: str, ingredients: List[Dict[str, str]]):
    """
    Adds ingredients to a user's shopping basket.
    
    Args:
        user_id: Identifier for the user's basket
        ingredients: List of ingredient dictionaries with name, quantity, and unit
    
    Returns:
        Information about the updated basket
    """
    # Create basket for user if it doesn't exist
    if user_id not in basket_db:
        basket_db[user_id] = []
    
    # Add ingredients to basket
    for ingredient in ingredients:
        basket_db[user_id].append(ingredient)
    
    return {
        'success': True,
        'user_id': user_id,
        'basket_count': len(basket_db[user_id]),
        'message': f"Added {len(ingredients)} ingredients to basket"
    }

def complete_purchase(user_id: str, payment_method: str = "credit_card", delivery_address: Optional[str] = None):
    """
    Completes the purchase for items in the user's basket.
    
    Args:
        user_id: Identifier for the user's basket
        payment_method: Method of payment (credit_card, paypal, etc.)
        delivery_address: Address for delivery (optional)
    
    Returns:
        Order confirmation details
    """
    # Check if basket exists and has items
    if user_id not in basket_db or not basket_db[user_id]:
        return {
            'success': False,
            'message': "Basket is empty or does not exist"
        }
    
    # Get basket items
    items = basket_db[user_id]
    
    # Generate order details
    order_id = f"ORDER-{hash(user_id + str(len(items)))}"
    total_price = sum(float(item.get('quantity', '1')) * 2.99 for item in items)  # Dummy pricing
    
    # In a real implementation, you would process payment here
    
    # Clear the basket after purchase
    purchased_items = basket_db[user_id].copy()
    basket_db[user_id] = []
    
    return {
        'success': True,
        'order_id': order_id,
        'user_id': user_id,
        'items_purchased': purchased_items,
        'item_count': len(purchased_items),
        'total_price': round(total_price, 2),
        'payment_method': payment_method,
        'delivery_address': delivery_address,
        'estimated_delivery': "3-5 business days",
        'message': "Purchase completed successfully!"
    }

root_agent = LlmAgent(name="Food_Agent",
                    model="gemini-2.0-flash",
                    description="This agent has all the capabilities to read a recipe from a website, understand its ingredients and place an order for them",
                    instruction="This agent has all the capabilities to read a recipe from a website, understand its ingredients and place an order for them",
                    tools=[scrape_recipe, extract_ingredients, add_to_basket, complete_purchase])
