from recommender import process_item_request
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

# Initialize OpenAI Model for response formatting
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

def main():
    print("Welcome to the AI E-commerce Recommender!")
    user_query = input("What kind of item are you looking for? ")
    
    # Get raw API response
    api_response = process_item_request(user_query)
    
    # Check if the API response is valid
    if not api_response or "results" not in api_response:
        print("\nSorry, we couldn't find any items matching your request.")
        return
    
    # Use LLM to format the response in a user-friendly way
    formatted_response = llm.invoke(
        f"""
        Based on the user's request: "{user_query}"
        
        Here is the raw API response: {api_response}
        
        Please format this into a user-friendly list of item recommendations.
        For each item, include:
        - Title and price
        - A brief description (if available)
        - Affiliate link (if available)
        
        Limit to the top 5 most relevant items.
        """
    )
    
    print("\nHere are your personalized item recommendations:")
    # Extract just the content from the response
    if hasattr(formatted_response, 'content'):
        print(formatted_response.content)
    else:
        print(str(formatted_response))

if __name__ == "__main__":
    main()