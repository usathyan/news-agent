from datetime import datetime
from typing import Any


class MarkdownGenerator:
    """Generate markdown reports from collected data"""

    def generate_report(self, data: dict[str, Any]) -> str:
        """Generate complete markdown report

        Args:
            data: Dictionary containing:
                - github_repos: List of repository dicts
                - hn_posts: List of HN post dicts
                - metadata: Report metadata

        Returns:
            Formatted markdown string
        """
        sections = []

        # Header
        sections.append(self._generate_header(data.get("metadata", {})))

        # GitHub section
        if data.get("github_repos"):
            sections.append(self.generate_github_section(data["github_repos"]))

        # Hacker News section
        if data.get("hn_posts"):
            sections.append(self.generate_hn_section(data["hn_posts"]))

        # Summary
        sections.append(self._generate_summary(data))

        return "\n\n---\n\n".join(sections)

    def _generate_header(self, metadata: dict[str, Any]) -> str:
        """Generate report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        return f"""# News Agent Report

**Generated:** {timestamp}
**Analysis Depth:** {metadata.get('analysis_depth', 'medium')}
**Sources:** {', '.join(metadata.get('sources', []))}"""

    def generate_github_section(self, repos: list[dict[str, Any]]) -> str:
        """Generate GitHub trending repositories section"""
        lines = [f"## GitHub Trending Repositories (Top {len(repos)})"]

        for i, repo in enumerate(repos, 1):
            lines.append(f"\n### {i}. [{repo['name']}]({repo['url']})")
            lines.append(f"**Description:** {repo.get('description', 'N/A')}")

            # Stats line
            stats = [
                f"⭐ {repo.get('stars', 0):,} stars",
                f"🔱 {repo.get('forks', 0):,} forks"
            ]

            if repo.get('language'):
                stats.append(f"💻 {repo['language']}")

            if repo.get('stars_today'):
                stats.append(f"📈 +{repo['stars_today']} stars today")

            lines.append(f"**Stats:** {' | '.join(stats)}")

            # Analysis
            if repo.get('analysis'):
                lines.append(f"**Analysis:** {repo['analysis']}")

        return "\n".join(lines)

    def generate_hn_section(self, posts: list[dict[str, Any]]) -> str:
        """Generate Hacker News section"""
        lines = [f"## Hacker News - AI/ML/GenAI Topics (Top {len(posts)})"]

        for i, post in enumerate(posts, 1):
            lines.append(f"\n### {i}. [{post['title']}]({post.get('hn_url', '#')})")

            if post.get('url'):
                lines.append(f"**Link:** {post['url']}")

            # Stats
            stats = [
                f"{post.get('score', 0)} points",
                f"{post.get('comments_count', 0)} comments"
            ]
            lines.append(f"**Stats:** {' | '.join(stats)}")

            # Summary
            if post.get('summary'):
                lines.append(f"**Summary:** {post['summary']}")

            # Discussion highlights
            if post.get('discussion'):
                lines.append(f"**Discussion Highlights:** {post['discussion']}")

        return "\n".join(lines)

    def _generate_summary(self, data: dict[str, Any]) -> str:
        """Generate report summary"""
        lines = ["## Summary"]

        github_count = len(data.get("github_repos", []))
        hn_count = len(data.get("hn_posts", []))

        if github_count:
            lines.append(f"- **GitHub:** {github_count} trending repositories analyzed")

        if hn_count:
            lines.append(f"- **Hacker News:** {hn_count} AI/ML topics curated")

        metadata = data.get("metadata", {})
        if metadata.get("sources"):
            sources_str = ", ".join(metadata["sources"])
            lines.append(f"- **Sources:** {sources_str}")

        return "\n".join(lines)
