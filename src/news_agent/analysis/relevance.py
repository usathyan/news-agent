import json
import re
from typing import Any
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import AnalysisConfig


class RelevanceScorer:
    """Score content relevance using LLM"""

    def __init__(self, llm_provider: LLMProvider, config: AnalysisConfig):
        self.llm = llm_provider
        self.config = config

    def score_hn_post(self, post: dict[str, Any], topics: list[str]) -> float:
        """Score a Hacker News post's relevance to specified topics

        Args:
            post: Post dictionary with title, url, text
            topics: List of topics to check relevance against

        Returns:
            Relevance score between 0.0 and 1.0
        """
        prompt = self._build_relevance_prompt(post, topics)

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.llm.complete_json(messages, temperature=0.3)
        result = self._extract_json(response)

        return float(result.get("relevance_score", 0.0))

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from text, handling markdown code blocks and extra text"""
        # Try to parse as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in text
        brace_match = re.search(r'\{.*\}', text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: return default
        return {"relevance_score": 0.0, "reasoning": "Failed to parse response", "key_topics": []}

    def _build_relevance_prompt(self, post: dict[str, Any], topics: list[str]) -> str:
        """Build prompt for relevance scoring"""
        topics_str = ", ".join(topics)

        return f"""Score the relevance of this Hacker News post to topics: {topics_str}

Post Title: {post.get('title', 'N/A')}
Post URL: {post.get('url', 'N/A')}
Post Text: {post.get('text', 'N/A')[:500]}

Analyze how relevant this post is to {topics_str}. Consider:
- Direct mentions or discussions of these topics
- Related concepts, tools, or techniques
- Practical applications or research
- Community interest and significance

Return a JSON object with:
{{
  "relevance_score": <float between 0.0 and 1.0>,
  "reasoning": "<brief explanation>",
  "key_topics": ["<topic1>", "<topic2>"]
}}

Score 1.0 = Highly relevant (directly about topic)
Score 0.5 = Moderately relevant (tangentially related)
Score 0.0 = Not relevant (unrelated)"""
