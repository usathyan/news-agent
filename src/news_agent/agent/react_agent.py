import logging
from typing import Any
from news_agent.config.models import Config
from news_agent.agent.tools import ToolRegistry
from news_agent.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


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
        logger.info("🔍 Starting GitHub data collection...")

        # Fetch trending repos
        logger.info("📡 Calling GitHub API to fetch trending repositories...")
        result = self.tools.tools["fetch_github_trending"](no_cache=no_cache)
        repos = result["data"]
        logger.info(f"✓ Retrieved {len(repos)} trending repositories")

        # Normalize popularity scores (stars)
        if repos:
            # TODO: Add analysis via LLM for project popularity
            logger.debug(f"   Top repo: {repos[0].get('name')} ({repos[0].get('stars')} stars)")
            pass

        # Take top N
        top_repos = repos[:self.config.analysis.top_n]
        logger.info(f"📊 Selected top {len(top_repos)} repositories for report")
        return top_repos

    def _collect_hn_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """Collect and analyze Hacker News data"""
        logger.info("🔍 Starting Hacker News data collection...")
        all_posts = []

        # Fetch from configured endpoints
        for endpoint in self.config.sources.hackernews.endpoints:
            logger.info(f"📡 Fetching posts from HN endpoint: {endpoint}")
            result = self.tools.tools["fetch_hn_posts"](endpoint=endpoint, no_cache=no_cache)
            all_posts.extend(result["data"])
            logger.info(f"✓ Retrieved {len(result['data'])} posts from {endpoint}")

        logger.info(f"📚 Total posts collected: {len(all_posts)}")

        # Score relevance
        topics = self.config.sources.hackernews.filter_topics
        logger.info(f"🤖 Analyzing relevance to topics: {', '.join(topics)}")
        logger.info(f"   Calling LLM to score {len(all_posts)} posts...")
        scored_posts = self.tools.tools["score_relevance"](all_posts, topics)
        logger.info(f"✓ Relevance scoring complete")

        # Filter by relevance threshold
        relevant_posts = [p for p in scored_posts if p.get("relevance_score", 0) > 0.5]
        logger.info(f"🔬 Filtered to {len(relevant_posts)} posts with relevance > 0.5")

        # Rank posts
        logger.info(f"📊 Ranking {len(relevant_posts)} relevant posts...")
        ranked_posts = self.tools.tools["rank_items"](relevant_posts)
        logger.info(f"✓ Ranking complete (strategy: {self.config.ranking.strategy})")

        # Take top N
        top_posts = ranked_posts[:self.config.analysis.top_n]
        logger.info(f"📝 Selected top {len(top_posts)} posts for report")
        return top_posts
