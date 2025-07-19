import os
import json
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
                    model='gpt-4',
                    messages=[
                        {
                            'role': 'system',
                            'content': (
                                'You are a financial analyst assistant. Given a news article or '
                                'report, your task is to:\n'
                                '1. Evaluate the sentiment (-1 to 1),\n'
                                '2. Identify the specific public companies, sectors, or ETFs most '
                                'likely to be affected,\n'
                                '3. Estimate whether the impact is likely to be short-term, '
                                'medium-term, or long-term,\n'
                                '4. Provide a confidence score (0–100%) in your prediction,\n'
                                '5. Optionally suggest historical analogs or precedent if available.\n\n'
                                'Only provide JSON output with the following keys:\n'
                                '- sentiment\n'
                                '- affected_entities\n'
                                '- impact_duration\n'
                                '- confidence_score\n'
                                '- rationale\n'
                                '- precedent (optional)'
                            )
                        },
                        {'role': 'user', 'content': text}
                    ]
                )
                content = response.choices[0].message.content.strip()
                try:
                    data = json.loads(content)
                    score = float(data.get('sentiment', 0))
                except Exception:
                    score = 0.0
            except Exception:
                score = 0.0
            sentiments.append(score)
        return sentiments
