from typing import Any, Callable
from news_agent.mcp.github_client import GitHubMCPClient
from news_agent.mcp.hn_client import HackerNewsMCPClient
from news_agent.analysis.relevance import RelevanceScorer
from news_agent.analysis.ranking import Ranker
from news_agent.cache.manager import CacheManager


class ToolRegistry:
    """Registry of tools available to the agent"""

    def __init__(
        self,
        github_client: GitHubMCPClient,
        hn_client: HackerNewsMCPClient,
        relevance_scorer: RelevanceScorer,
        ranker: Ranker,
        cache_manager: CacheManager
    ):
        self.github_client = github_client
        self.hn_client = hn_client
        self.relevance_scorer = relevance_scorer
        self.ranker = ranker
        self.cache = cache_manager

        self.tools = self._register_tools()

    def _register_tools(self) -> dict[str, Callable]:
        """Register all available tools"""
        return {
            "fetch_github_trending": self._fetch_github_trending,
            "fetch_hn_posts": self._fetch_hn_posts,
            "score_relevance": self._score_relevance,
            "rank_items": self._rank_items,
        }

    def _fetch_github_trending(self, **kwargs: Any) -> dict[str, Any]:
        """Tool: Fetch GitHub trending repositories"""
        cache_key = "github_trending"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached and not kwargs.get("no_cache"):
            return {"source": "cache", "data": cached}

        # Fetch fresh data
        repos = self.github_client.fetch_trending_repositories()

        # Cache results
        self.cache.set(cache_key, repos)

        return {"source": "mcp", "data": repos}

    def _fetch_hn_posts(self, endpoint: str = "newest", **kwargs: Any) -> dict[str, Any]:
        """Tool: Fetch Hacker News posts"""
        cache_key = f"hn_{endpoint}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached and not kwargs.get("no_cache"):
            return {"source": "cache", "data": cached}

        # Fetch fresh data
        posts = self.hn_client.fetch_posts(endpoint)

        # Cache results
        self.cache.set(cache_key, posts)

        return {"source": "mcp", "data": posts}

    def _score_relevance(self, items: list[dict[str, Any]], topics: list[str], **kwargs: Any) -> list[dict[str, Any]]:
        """Tool: Score relevance of items"""
        for item in items:
            score = self.relevance_scorer.score_hn_post(item, topics)
            item["relevance_score"] = score

        return items

    def _rank_items(self, items: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Tool: Rank items based on configured strategy"""
        return self.ranker.rank(items)
