import pytest
from news_agent.mcp.github_client import GitHubMCPClient
from news_agent.config.models import GitHubSourceConfig


@pytest.fixture
def github_config():
    return GitHubSourceConfig(
        enabled=True,
        mcp_server="remote",
        categories=["repositories"]
    )


@pytest.mark.skip(reason="Requires live GitHub API access and rate limits")
def test_fetch_trending_repositories(github_config):
    """Test fetching trending repositories via MCP"""
    client = GitHubMCPClient(github_config)

    repos = client.fetch_trending_repositories()

    assert len(repos) > 0
    assert "name" in repos[0]
    assert "url" in repos[0]
    assert "stars" in repos[0]
    assert "description" in repos[0]
