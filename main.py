from recommender import process_item_request
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

# Initialize OpenAI Model for response formatting
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

def main():
    print("Welcome to the AI E-commerce Recommender!")
    user_query = input("What kind of item are you looking for? ")
    
    # Clean up the user input
    user_query = user_query.strip()
    
    # Get raw API response
    api_response = process_item_request(user_query)
    
    # Add more detailed error handling
    if not api_response:
        print("\nSorry, there was an error processing your request.")
        return
    
    if "results" not in api_response or not api_response["results"]:
        print("\nSorry, we couldn't find any items matching your request.")
        print("Try being more specific or using different keywords.")
        print("Available categories: electronics, books, toys, games, kitchen, home, beauty, clothing, sports, fitness, office")
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
        - URL link to the item on Amazon
        
        Limit to the top 10 most relevant items. If no items are found, suggest alternatives.
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