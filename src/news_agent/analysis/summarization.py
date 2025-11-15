from typing import Any
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import AnalysisConfig


class Summarizer:
    """Generate summaries of articles and comments"""

    def __init__(self, llm_provider: LLMProvider, config: AnalysisConfig):
        self.llm = llm_provider
        self.config = config

    def summarize_article(self, article: dict[str, Any]) -> str:
        """Summarize an article based on configured depth

        Args:
            article: Article dictionary with title, url, text

        Returns:
            Summary string
        """
        prompt = self._build_article_summary_prompt(article)

        messages = [
            {"role": "user", "content": prompt}
        ]

        max_tokens = self._get_max_tokens_for_depth()
        return self.llm.complete(messages, temperature=0.5, max_tokens=max_tokens)

    def summarize_comments(self, comments: list[dict[str, Any]]) -> str:
        """Summarize key themes from comments

        Args:
            comments: List of comment dictionaries

        Returns:
            Summary of comment themes
        """
        if not comments:
            return "No comments available"

        prompt = self._build_comments_summary_prompt(comments)

        messages = [
            {"role": "user", "content": prompt}
        ]

        max_tokens = self._get_max_tokens_for_depth()
        return self.llm.complete(messages, temperature=0.5, max_tokens=max_tokens)

    def _build_article_summary_prompt(self, article: dict[str, Any]) -> str:
        """Build prompt for article summarization"""
        depth_instructions = {
            "lightweight": "Provide a one-sentence summary (max 50 words).",
            "medium": "Provide a concise summary (2-3 sentences, max 100 words) covering key points.",
            "deep": "Provide a comprehensive summary (4-5 sentences, max 200 words) including context, implications, and significance."
        }

        instruction = depth_instructions.get(self.config.depth, depth_instructions["medium"])

        return f"""Summarize this article:

Title: {article.get('title', 'N/A')}
URL: {article.get('url', 'N/A')}
Content: {article.get('text', 'N/A')[:2000]}

{instruction}"""

    def _build_comments_summary_prompt(self, comments: list[dict[str, Any]]) -> str:
        """Build prompt for comment summarization"""
        comments_text = "\n\n".join([
            f"Comment by {c.get('by', 'unknown')}: {c.get('text', '')[:300]}"
            for c in comments[:10]  # Limit to top 10 comments
        ])

        depth_instructions = {
            "lightweight": "List 2-3 key discussion themes (one sentence).",
            "medium": "Summarize main discussion themes and notable perspectives (2-3 sentences).",
            "deep": "Provide detailed analysis of discussion themes, sentiment, consensus/disagreement, and notable insights (4-5 sentences)."
        }

        instruction = depth_instructions.get(self.config.depth, depth_instructions["medium"])

        return f"""Analyze these comments and {instruction}

{comments_text}"""

    def _get_max_tokens_for_depth(self) -> int:
        """Get max tokens based on analysis depth"""
        return {
            "lightweight": 128,
            "medium": 256,
            "deep": 512
        }.get(self.config.depth, 256)
