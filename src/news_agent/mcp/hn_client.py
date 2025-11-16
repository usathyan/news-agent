import asyncio
import logging
from typing import Any, Literal
from news_agent.config.models import HackerNewsSourceConfig
import httpx

logger = logging.getLogger(__name__)


class HackerNewsMCPClient:
    """Client for interacting with Hacker News API"""

    def __init__(self, config: HackerNewsSourceConfig):
        self.config = config
        self.base_url = "https://hacker-news.firebaseio.com/v0"

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
        return asyncio.run(self._fetch_posts_async(endpoint, limit))

    async def _fetch_posts_async(self, endpoint: str, limit: int) -> list[dict[str, Any]]:
        """Async implementation to fetch HN posts"""
        try:
            # Map endpoint names to HN API endpoints
            endpoint_map = {
                "newest": "newstories",
                "show": "showstories",
                "ask": "askstories",
                "job": "jobstories"
            }
            api_endpoint = endpoint_map.get(endpoint, "newstories")

            logger.info(f"Fetching {endpoint} stories from Hacker News (limit: {limit})")

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Get list of story IDs
                response = await client.get(f"{self.base_url}/{api_endpoint}.json")

                if response.status_code != 200:
                    logger.error(f"HN API error: {response.status_code}")
                    return []

                story_ids = response.json()[:limit]  # Limit to requested count

                # Step 2: Fetch details for each story in parallel
                tasks = [
                    self._fetch_item_details(client, story_id)
                    for story_id in story_ids
                ]
                stories = await asyncio.gather(*tasks)

                # Step 3: Filter out None values and apply topic filtering
                valid_stories = [s for s in stories if s is not None]

                # Apply topic filtering if configured
                if self.config.filter_topics:
                    filtered_stories = self._filter_by_topics(valid_stories)
                    logger.info(
                        f"Filtered {len(valid_stories)} stories to {len(filtered_stories)} "
                        f"matching topics: {self.config.filter_topics}"
                    )
                    return filtered_stories

                logger.info(f"Fetched {len(valid_stories)} stories from HN")
                return valid_stories

        except Exception as e:
            logger.error(f"Error fetching HN posts: {e}")
            return []

    async def _fetch_item_details(self, client: httpx.AsyncClient, item_id: int) -> dict[str, Any] | None:
        """Fetch details for a single HN item"""
        try:
            response = await client.get(f"{self.base_url}/item/{item_id}.json")

            if response.status_code != 200:
                return None

            item = response.json()

            # Skip if not a story or if deleted/dead
            if not item or item.get("type") != "story" or item.get("deleted") or item.get("dead"):
                return None

            return {
                "id": item.get("id"),
                "title": item.get("title", ""),
                "url": item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}",
                "score": item.get("score", 0),
                "by": item.get("by", "unknown"),
                "time": item.get("time", 0),
                "descendants": item.get("descendants", 0),
                "text": item.get("text", "")  # For Ask HN posts
            }

        except Exception as e:
            logger.debug(f"Error fetching item {item_id}: {e}")
            return None

    def _filter_by_topics(self, stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter stories by configured topics"""
        if not self.config.filter_topics:
            return stories

        filtered = []
        topics_lower = [t.lower() for t in self.config.filter_topics]

        for story in stories:
            title_lower = story.get("title", "").lower()
            text_lower = story.get("text", "").lower()

            # Check if any topic appears in title or text
            if any(topic in title_lower or topic in text_lower for topic in topics_lower):
                filtered.append(story)

        return filtered

    def fetch_comments(self, post_id: int) -> list[dict[str, Any]]:
        """Fetch comments for a post

        Returns:
            List of comment dictionaries
        """
        # TODO: Implement if needed for future features
        return []
