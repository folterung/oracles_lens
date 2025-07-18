import os
import requests
from typing import List, Dict

NEWS_API_URL = 'https://newsapi.org/v2/everything'

class NewsFetcher:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError('NEWS_API_KEY not set')

    def fetch(self, query: str, page_size: int = 5) -> List[Dict]:
        params = {
            'q': query,
            'language': 'en',
            'pageSize': page_size,
            'apiKey': self.api_key,
        }
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('articles', [])
