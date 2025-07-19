import os
import json
from openai import OpenAI
from typing import List, Dict, Any

class SentimentAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError('OPENAI_API_KEY not set')
        self.client = OpenAI(api_key=self.api_key)

    def analyze(self, texts: List[str], symbol: str = '') -> List[Dict[str, Any]]:
        """Return structured sentiment insights for each provided text."""
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
                    # ensure required keys exist even if missing from response
                    data = {
                        'sentiment': data.get('sentiment', 0.0),
                        'affected_entities': data.get('affected_entities', []),
                        'impact_duration': data.get('impact_duration', ''),
                        'confidence_score': data.get('confidence_score', 0.0),
                        'rationale': data.get('rationale', ''),
                        **({'precedent': data.get('precedent')} if 'precedent' in data else {})
                    }
                except Exception:
                    # fallback structure on parsing failure
                    data = {
                        'sentiment': 0.0,
                        'affected_entities': [],
                        'impact_duration': '',
                        'confidence_score': 0.0,
                        'rationale': '',
                    }
            except Exception:
                data = {
                    'sentiment': 0.0,
                    'affected_entities': [],
                    'impact_duration': '',
                    'confidence_score': 0.0,
                    'rationale': '',
                }
            sentiments.append(data)
        return sentiments
