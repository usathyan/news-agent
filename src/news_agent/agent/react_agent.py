from typing import Any
from news_agent.config.models import Config
from news_agent.agent.tools import ToolRegistry
from news_agent.llm.provider import LLMProvider


class NewsAgent:
    """ReACT agent using Claude Agent SDK"""

    def __init__(
        self,
        config: Config,
        tool_registry: ToolRegistry,
        llm_provider: LLMProvider
    ):
        self.config = config
        self.tools = tool_registry
        self.llm = llm_provider

        # TODO: Initialize Claude Agent SDK client
        # This will use the SDK's MCP integration

    def run(self, no_cache: bool = False) -> dict[str, Any]:
        """Execute the news aggregation workflow

        Returns:
            Dictionary with collected and analyzed data
        """
        results = {
            "github_repos": [],
            "hn_posts": [],
            "metadata": {
                "sources": [],
                "analysis_depth": self.config.analysis.depth
            }
        }

        # GitHub collection
        if self.config.sources.github.enabled:
            github_data = self._collect_github_data(no_cache)
            results["github_repos"] = github_data
            results["metadata"]["sources"].append("github")

        # Hacker News collection
        if self.config.sources.hackernews.enabled:
            hn_data = self._collect_hn_data(no_cache)
            results["hn_posts"] = hn_data
            results["metadata"]["sources"].append("hackernews")

        return results

    def _collect_github_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """Collect and analyze GitHub trending data"""
        # Fetch trending repos
        result = self.tools.tools["fetch_github_trending"](no_cache=no_cache)
        repos = result["data"]

        # Normalize popularity scores (stars)
        if repos:
            # TODO: Add analysis via LLM for project popularity
            pass

        # Take top N
        return repos[:self.config.analysis.top_n]

    def _collect_hn_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """Collect and analyze Hacker News data"""
        all_posts = []

        # Fetch from configured endpoints
        for endpoint in self.config.sources.hackernews.endpoints:
            result = self.tools.tools["fetch_hn_posts"](endpoint=endpoint, no_cache=no_cache)
            all_posts.extend(result["data"])

        # Score relevance
        topics = self.config.sources.hackernews.filter_topics
        scored_posts = self.tools.tools["score_relevance"](all_posts, topics)

        # Filter by relevance threshold
        relevant_posts = [p for p in scored_posts if p.get("relevance_score", 0) > 0.5]

        # Rank posts
        ranked_posts = self.tools.tools["rank_items"](relevant_posts)

        # Take top N
        return ranked_posts[:self.config.analysis.top_n]
