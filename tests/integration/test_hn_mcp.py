import pytest
from news_agent.mcp.hn_client import HackerNewsMCPClient
from news_agent.config.models import HackerNewsSourceConfig


@pytest.fixture
def hn_config():
    return HackerNewsSourceConfig(
        enabled=True,
        mcp_server="local",
        endpoints=["newest"],
        filter_topics=[]  # No filtering for test - just verify API works
    )


def test_fetch_newest_posts(hn_config):
    """Test fetching newest posts via HN API"""
    client = HackerNewsMCPClient(hn_config)

    posts = client.fetch_posts("newest", limit=10)

    assert len(posts) > 0
    assert "title" in posts[0]
    assert "url" in posts[0]
    assert "score" in posts[0]
