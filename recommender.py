import os
import yaml
import time
import requests
from langchain.chains.api.base import APIChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config import OPENAI_API_KEY, APIFY_API_KEY

# Initialize OpenAI Model
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

# Load OpenAPI spec from YAML file
def load_api_docs():
    yaml_path = os.path.join(os.path.dirname(__file__), 'doc.yaml')
    with open(yaml_path, 'r') as file:
        spec = yaml.safe_load(file)
    
    # Convert to string format expected by LangChain
    api_docs = f"""
    BASE_URL: {spec['servers'][0]['url']}
    
    ENDPOINTS:
    """
    
    # Add each endpoint from the spec
    for path, methods in spec['paths'].items():
        for method, details in methods.items():
            api_docs += f"  - {method.upper()} {path}\n"
            api_docs += f"    Description: {details.get('description', details.get('summary', ''))}\n"
            
            # Add parameters
            if 'parameters' in details:
                api_docs += "    Parameters:\n"
                for param in details['parameters']:
                    api_docs += f"      - {param['name']} ({param['in']}): {param.get('description', '')}\n"
    
    return api_docs

# Define custom prompt template for item queries
item_api_prompt = PromptTemplate(
    input_variables=["query", "api_docs"],
    template="""
    You are an AI assistant that helps users find items using the Apify Amazon Bestsellers Scraper API.
    Based on the user's request, determine which API endpoint to use and how to format the request.
    
    User Request: {query}
    
    API Documentation:
    {api_docs}
    
    Your task is to:
    1. Determine which API endpoint best matches the user's request
    2. Format the request properly for that endpoint
    3. Include the API key parameter in your request
    
    API Request:
    """
)

# Extract item keywords for better searching
def extract_keywords(user_query):
    """Extract relevant keywords from a user query for better item search"""
    # Map common request patterns to relevant search terms
    query_mapping = {
        "electronics": "electronics",
        "books": "books",
        "clothing": "clothing",
        "shoes": "shoes",
        "home": "home",
        "kitchen": "kitchen",
        "garden": "garden",
        "toys": "toys",
        "games": "games",
        "sports": "sports",
        "fitness": "fitness",
        "beauty": "beauty",
        "health": "health",
        "baby": "baby",
        "pet": "pet",
        "office": "office",
        "tools": "tools",
        "automotive": "automotive"
    }
    
    # Convert query to lowercase for matching
    query_lower = user_query.lower()
    
    # Check for keyword matches
    for key, value in query_mapping.items():
        if key in query_lower:
            return value
    
    # If no specific matches, return the original query but remove common phrases
    cleaned_query = query_lower.replace("i want", "").replace("item that will", "").replace("looking for", "")
    cleaned_query = cleaned_query.replace("i'm looking for", "").replace("can you recommend", "")
    cleaned_query = cleaned_query.strip()
    
    return cleaned_query

def search_amazon_products(query):
    """Search for products on Amazon using the Apify Amazon Product Scraper API."""
    # Start a new run
    run_url = "https://api.apify.com/v2/acts/junglee~amazon-bestsellers/runs"
    
    # Map query to appropriate category URL
    category_mapping = {
        "electronics": "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics",
        "books": "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books",
        "toys": "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games",
        "games": "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games",
        "kitchen": "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen",
        "home": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden",
        "beauty": "https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty",
        "clothing": "https://www.amazon.com/Best-Sellers-Clothing-Shoes-Jewelry/zgbs/fashion",
        "sports": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods",
        "fitness": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods",
        "office": "https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products"
    }
    
    category_url = category_mapping.get(query.lower(), "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics")
    
    payload = {
        "token": APIFY_API_KEY
    }
    
    json_data = {
        "categoryUrls": [category_url],
        "maxItems": 10  # Limit to 10 items to save costs
    }
    
    # Start the run
    response = requests.post(run_url, params=payload, json=json_data)
    
    if response.status_code != 201:
        print(f"Failed to start actor run: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    
    # Extract run ID and dataset ID
    run_data = response.json().get("data", {})
    run_id = run_data.get("id")
    dataset_id = run_data.get("defaultDatasetId")
    
    if not run_id or not dataset_id:
        print("Missing run ID or dataset ID")
        return []
    
    print(f"Run started with ID: {run_id}")
    print(f"Dataset ID: {dataset_id}")
    
    # Poll for run status
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    max_attempts = 30  # Adjust based on expected run time
    
    print("Waiting for run to complete...")
    for attempt in range(max_attempts):
        time.sleep(5)  # Wait 5 seconds between status checks
        
        status_response = requests.get(status_url, params=payload)
        if status_response.status_code != 200:
            print(f"Failed to get run status: {status_response.status_code}")
            continue
        
        status_data = status_response.json().get("data", {})
        status = status_data.get("status")
        
        print(f"Run status: {status} (attempt {attempt+1}/{max_attempts})")
        
        if status == "SUCCEEDED":
            print("Run completed successfully!")
            break
        elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"Run failed with status: {status}")
            return []
    else:
        print("Timed out waiting for run to complete")
        return []
    
    # Get dataset items
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    dataset_response = requests.get(dataset_url, params=payload)
    
    if dataset_response.status_code != 200:
        print(f"Failed to get dataset items: {dataset_response.status_code}")
        print(f"Response: {dataset_response.text}")
        return []
    
    items = dataset_response.json()
    print(f"Retrieved {len(items)} items from dataset")
    
    return items

def process_item_request(user_query):
    """
    Process user's item request through the Apify API.
    """
    try:
        # Extract keywords from the user query
        search_term = extract_keywords(user_query)
        print(f"Searching for: {search_term}")
        
        # Search Amazon products using the Apify API
        items = search_amazon_products(search_term)
        
        # Format the items into a standardized structure
        formatted_results = []
        
        for item in items:
            # Skip items with missing essential data
            if not item.get('name'):
                continue
                
            # Extract price (handle different formats)
            price = item.get('price', 'Price not available')
            
            formatted_item = {
                'title': item.get('name', 'Unknown'),
                'price': price,
                'url': item.get('url', ''),
                'rating': item.get('stars', 'No rating'),
                'reviews': item.get('reviewsCount', 'No reviews'),
                'category': item.get('categoryName', 'Unknown category')
            }
            formatted_results.append(formatted_item)
        
        return {"results": formatted_results}
        
    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return {"results": []}