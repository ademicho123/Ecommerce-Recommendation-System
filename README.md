# LLM Movie Recommendation System

A smart movie recommendation system that uses The Movie Database (TMDb) API and language models to provide personalized movie suggestions based on natural language queries.

## Overview

This project combines the power of TMDb's movie database with OpenAI's language models to create an intelligent movie recommendation system that understands conversational requests. It can:

- Search for movies based on natural language queries (e.g., "I want a movie that will make me laugh")
- Convert user intentions into appropriate search terms
- Show popular movies
- Display top-rated movies
- Format results in a user-friendly way

## Requirements

- Python 3.7+
- API keys for:
  - The Movie Database (TMDb) - Get it from [TMDb website](https://www.themoviedb.org/settings/api)
  - OpenAI - Get it from [OpenAI's platform](https://platform.openai.com/)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ademicho123/LLM-Movie-Recommendation-System.git
   cd LLM-Movie-Recommendation-System
   ```

2. Install the required packages:
   ```
   pip install requests python-dotenv langchain langchain-openai pyyaml
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   MOVIE_DB_API_KEY=your_tmdb_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## File Structure

- `main.py` - Main application entry point and user interface
- `api_utils.py` - Functions for direct interaction with TMDb API
- `llm_recommender.py` - Language model integration for intelligent query processing
- `config.py` - Configuration and environment variables loading
- `moviedb_doc.yaml` - OpenAPI specification for TMDb API

## Usage

Run the application with:
```
python main.py
```

You will be prompted to enter a query. The system understands natural language requests such as:
- "I want a movie that will make me laugh"
- "Show me popular movies"
- "What are the top rated movies?"
- "Find me something scary"
- "I'm looking for a romantic film"

The system will intelligently process your request, extract relevant keywords, search the TMDb database, and return formatted recommendations.

## How It Works

1. The user enters a natural language query
2. The system extracts relevant keywords (e.g., "laugh" → "comedy")
3. It queries the TMDb API using the appropriate endpoint
4. Results are formatted using OpenAI's language model
5. Recommendations are displayed with title, year, description, and rating

## API Specification

The `moviedb_doc.yaml` file contains the OpenAPI 3.0 specification for the TMDb API endpoints used in this project. This provides documentation for the API structure and can be used for testing or client generation.

## Error Handling

The application includes robust error handling for:
- API connection issues
- Empty search results
- Malformed queries
- Missing or incomplete movie data

## Future Improvements

- Add more detailed movie information (cast, director, etc.)
- Implement advanced genre filtering and combinations
- Create user profiles for personalized recommendations
- Develop a web interface or chat interface
- Expand API coverage to include TV shows and documentaries
- Add streaming service availability information

## License

MIT

## Acknowledgments

- [The Movie Database (TMDb)](https://www.themoviedb.org/) for providing the movie data API
- [LangChain](https://langchain.com/) for simplifying LLM integration
- [OpenAI](https://openai.com/) for their powerful language models