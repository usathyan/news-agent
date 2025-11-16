import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any
from news_agent.config.models import GitHubSourceConfig
import httpx

logger = logging.getLogger(__name__)


class GitHubMCPClient:
    """Client for interacting with GitHub via MCP or direct API"""

    def __init__(self, config: GitHubSourceConfig):
        self.config = config
        self.github_token = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            logger.warning("No GITHUB_PAT or GITHUB_TOKEN found - API calls may be rate limited")

    def fetch_trending_repositories(self, time_range: str = "daily") -> list[dict[str, Any]]:
        """Fetch trending repositories from GitHub

        Args:
            time_range: One of "daily", "weekly", "monthly"

        Returns:
            List of repository dictionaries with keys:
            - name: Repository name (owner/repo)
            - url: Repository URL
            - description: Repository description
            - stars: Star count
            - forks: Fork count
            - language: Primary language
            - stars_today: Stars gained today
        """
        return asyncio.run(self._fetch_trending_repos_async(time_range))

    async def _fetch_trending_repos_async(self, time_range: str) -> list[dict[str, Any]]:
        """Async implementation to fetch trending repos"""
        try:
            # Calculate date range for trending
            days_map = {"daily": 1, "weekly": 7, "monthly": 30}
            days = days_map.get(time_range, 1)
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            # Build search query for trending repos
            query = f"created:>{since_date} stars:>50 sort:stars"

            logger.info(f"Searching GitHub for: {query}")

            # Use GitHub REST API directly (simpler than MCP for now)
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/search/repositories",
                    params={
                        "q": f"created:>{since_date} stars:>50",
                        "sort": "stars",
                        "order": "desc",
                        "per_page": 25
                    },
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    repos = []
                    for item in data.get("items", [])[:25]:
                        repos.append({
                            "name": item.get("full_name", ""),
                            "url": item.get("html_url", ""),
                            "description": item.get("description", "") or "No description",
                            "stars": item.get("stargazers_count", 0),
                            "forks": item.get("forks_count", 0),
                            "language": item.get("language", "") or "Unknown",
                            "stars_today": 0  # GitHub API doesn't provide daily star delta
                        })
                    logger.info(f"Found {len(repos)} trending repositories")
                    return repos
                else:
                    logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching trending repos: {e}")
            return []

    def fetch_trending_developers(self, time_range: str = "daily") -> list[dict[str, Any]]:
        """Fetch trending developers from GitHub

        Returns:
            List of developer dictionaries
        """
        # TODO: Implement after repos works
        return []
