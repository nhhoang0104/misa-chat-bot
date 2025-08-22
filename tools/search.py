import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

# Load .env file
load_dotenv()
# Khởi tạo tool
tavily_search_tool = TavilySearch(
            max_results=5,
            topic="general"
        )

