import os
import openai
from typing import List

class SentimentAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError('OPENAI_API_KEY not set')
        openai.api_key = self.api_key

    def analyze(self, texts: List[str]) -> List[float]:
        sentiments = []
        for text in texts:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'Rate the sentiment of the following text from -1 (very negative) to 1 (very positive). Reply with just the number.'},
                    {'role': 'user', 'content': text}
                ]
            )
            try:
                score = float(response.choices[0].message['content'].strip())
            except Exception:
                score = 0.0
            sentiments.append(score)
        return sentiments
