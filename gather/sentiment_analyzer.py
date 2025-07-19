import os
from openai import OpenAI
from typing import List

class SentimentAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError('OPENAI_API_KEY not set')
        self.client = OpenAI(api_key=self.api_key)

    def analyze(self, texts: List[str]) -> List[float]:
        sentiments = []
        for text in texts:
            try:
                response = self.client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'system', 'content': 'Rate the sentiment of the following text from -1 (very negative) to 1 (very positive). Reply with just the number.'},
                        {'role': 'user', 'content': text}
                    ]
                )
                score = float(response.choices[0].message.content.strip())
            except Exception:
                score = 0.0
            sentiments.append(score)
        return sentiments
