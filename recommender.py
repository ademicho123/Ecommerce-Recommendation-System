import os
import yaml
import requests
from langchain.chains.api.base import APIChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config import OPENAI_API_KEY, AMAZON_AFFILIATE_API_KEY, BOL_PLAZA_API_KEY

# Initialize OpenAI Model
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

# Load OpenAPI spec from YAML file
def load_api_docs():
    yaml_path = os.path.join(os.path.dirname(__file__), 'ecommerce_doc.yaml')
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
    You are an AI assistant that helps users find items using e-commerce affiliate APIs.
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

def search_amazon(query):
    """Search for items on Amazon using the affiliate API."""
    url = f"https://affiliate-api.amazon.com/search?query={query}&api_key={AMAZON_AFFILIATE_API_KEY}"
    response = requests.get(url)
    return response.json()

def search_bol_plaza(query):
    """Search for items on Bol Plaza using the affiliate API."""
    url = f"https://api.bolplaza.com/search?query={query}&api_key={BOL_PLAZA_API_KEY}"
    response = requests.get(url)
    return response.json()

def process_item_request(user_query):
    """
    Process user's item request through the LLM and API Chain.
    This lets the LLM determine which endpoint to use based on understanding the query.
    """
    try:
        # Extract keywords from the user query
        search_term = extract_keywords(user_query)
        print(f"Searching for: {search_term}")
        
        # Search both Amazon and Bol Plaza
        amazon_response = search_amazon(search_term)
        bol_plaza_response = search_bol_plaza(search_term)
        
        # Combine results
        combined_results = {
            "results": (amazon_response.get("results", []) + bol_plaza_response.get("results", []))[:5]
        }
        
        return combined_results
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return {"results": []}