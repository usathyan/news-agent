from typing import Any, Literal
from news_agent.config.models import HackerNewsSourceConfig


class HackerNewsMCPClient:
    """Client for interacting with Hacker News MCP server"""

    def __init__(self, config: HackerNewsSourceConfig):
        self.config = config
        # TODO: Initialize MCP connection

    def fetch_posts(
        self,
        endpoint: Literal["newest", "show", "ask", "job"],
        limit: int = 30
    ) -> list[dict[str, Any]]:
        """Fetch posts from Hacker News

        Args:
            endpoint: HN endpoint to query
            limit: Maximum number of posts to fetch

        Returns:
            List of post dictionaries with keys:
            - id: Post ID
            - title: Post title
            - url: Post URL (may be None for Ask HN)
            - score: Points/votes
            - by: Author username
            - time: Unix timestamp
            - descendants: Comment count
        """
        # TODO: Implement MCP call
        return []

    def fetch_comments(self, post_id: int) -> list[dict[str, Any]]:
        """Fetch comments for a post

        Returns:
            List of comment dictionaries
        """
        # TODO: Implement MCP call
        return []
