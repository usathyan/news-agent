from news_agent.output.terminal import TerminalDisplay


def test_display_github_preview():
    """Test rendering GitHub repos preview"""
    display = TerminalDisplay()

    repos = [
        {
            "name": "owner/repo",
            "stars": 1234,
            "forks": 567,
            "description": "Test description"
        }
    ]

    # Should not raise an error
    display.show_github_preview(repos, limit=5)


def test_display_progress():
    """Test progress indicators"""
    display = TerminalDisplay()

    # Should not raise an error
    display.show_progress("Fetching GitHub trending...")
    display.show_success("GitHub data fetched successfully")
    display.show_error("Test error message")
