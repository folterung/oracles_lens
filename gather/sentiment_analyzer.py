import os
import json
import re
from openai import OpenAI
from typing import List, Dict, Any

class SentimentAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError('OPENAI_API_KEY not set')
        self.client = OpenAI(api_key=self.api_key)

    def _parse_json(self, content: str) -> Dict[str, Any] | None:
        """Return a dict from a JSON string, trying to recover from malformed output."""
        try:
            return json.loads(content)
        except Exception:
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    return None
            return None

    def analyze(self, texts: List[str], symbol: str = '') -> List[Dict[str, Any]]:
        """Return structured sentiment insights for each provided text."""
        insights: List[Dict[str, Any]] = []
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
                parsed = self._parse_json(content)
                if not parsed:
                    # skip malformed output instead of crashing
                    continue
                data = {
                    'sentiment': float(parsed.get('sentiment', 0.0)),
                    'affected_entities': parsed.get('affected_entities', []),
                    'impact_duration': parsed.get('impact_duration', ''),
                    'confidence_score': float(parsed.get('confidence_score', 0.0)),
                    'rationale': parsed.get('rationale', ''),
                }
                if 'precedent' in parsed and parsed['precedent']:
                    data['precedent'] = parsed['precedent']
            except Exception:
                # skip this text if API call fails
                continue
            insights.append(data)
        return insights
