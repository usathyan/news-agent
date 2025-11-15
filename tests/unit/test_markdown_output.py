from datetime import datetime
from news_agent.output.markdown import MarkdownGenerator


def test_generate_github_section():
    """Test generating markdown for GitHub trending repos"""
    generator = MarkdownGenerator()

    repos = [
        {
            "name": "owner/repo-name",
            "url": "https://github.com/owner/repo-name",
            "description": "An awesome project",
            "stars": 1234,
            "forks": 567,
            "language": "Python",
            "stars_today": 150,
            "analysis": "This project is trending due to recent feature release."
        }
    ]

    markdown = generator.generate_github_section(repos)

    assert "## GitHub Trending Repositories" in markdown
    assert "owner/repo-name" in markdown
    assert "1,234" in markdown  # stars (with comma formatting)
    assert "567" in markdown  # forks


def test_generate_full_report():
    """Test generating complete report"""
    generator = MarkdownGenerator()

    data = {
        "github_repos": [
            {
                "name": "test/repo",
                "url": "https://github.com/test/repo",
                "description": "Test repo",
                "stars": 100,
                "forks": 20,
                "analysis": "Test analysis"
            }
        ],
        "hn_posts": [
            {
                "title": "Test Post",
                "url": "https://example.com",
                "hn_url": "https://news.ycombinator.com/item?id=123",
                "score": 50,
                "comments_count": 10,
                "summary": "Test summary",
                "discussion": "Test discussion"
            }
        ],
        "metadata": {
            "sources": ["github", "hackernews"],
            "analysis_depth": "medium"
        }
    }

    markdown = generator.generate_report(data)

    assert "# News Agent Report" in markdown
    assert "## GitHub Trending Repositories" in markdown
    assert "## Hacker News" in markdown
    assert "test/repo" in markdown
    assert "Test Post" in markdown
