from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


class TerminalDisplay:
    """Handle rich terminal output"""

    def __init__(self):
        self.console = Console()

    def show_github_preview(self, repos: list[dict[str, Any]], limit: int = 10) -> None:
        """Display GitHub repos preview in terminal"""
        table = Table(title="GitHub Trending Repositories", show_header=True)

        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Repository", style="magenta")
        table.add_column("Stars", style="green", justify="right")
        table.add_column("Forks", style="yellow", justify="right")
        table.add_column("Description", style="white")

        for i, repo in enumerate(repos[:limit], 1):
            table.add_row(
                str(i),
                repo.get("name", "N/A"),
                f"{repo.get('stars', 0):,}",
                f"{repo.get('forks', 0):,}",
                repo.get("description", "")[:60] + "..." if len(repo.get("description", "")) > 60 else repo.get("description", "")
            )

        self.console.print(table)

    def show_hn_preview(self, posts: list[dict[str, Any]], limit: int = 10) -> None:
        """Display HN posts preview in terminal"""
        table = Table(title="Hacker News - AI/ML/GenAI Topics", show_header=True)

        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Title", style="magenta")
        table.add_column("Score", style="green", justify="right")
        table.add_column("Comments", style="yellow", justify="right")

        for i, post in enumerate(posts[:limit], 1):
            table.add_row(
                str(i),
                post.get("title", "N/A")[:60] + "..." if len(post.get("title", "")) > 60 else post.get("title", ""),
                str(post.get("score", 0)),
                str(post.get("comments_count", 0))
            )

        self.console.print(table)

    def show_summary(self, summary: dict[str, Any]) -> None:
        """Display summary panel"""
        summary_text = "\n".join([
            f"[bold]GitHub Repos:[/bold] {summary.get('github_count', 0)}",
            f"[bold]HN Posts:[/bold] {summary.get('hn_count', 0)}",
            f"[bold]Analysis Depth:[/bold] {summary.get('depth', 'medium')}",
            f"[bold]Report Saved:[/bold] {summary.get('report_path', 'N/A')}"
        ])

        panel = Panel(summary_text, title="Summary", border_style="green")
        self.console.print(panel)

    def show_progress(self, message: str) -> None:
        """Show progress message"""
        self.console.print(f"[blue]⏳[/blue] {message}")

    def show_success(self, message: str) -> None:
        """Show success message"""
        self.console.print(f"[green]✓[/green] {message}")

    def show_error(self, message: str) -> None:
        """Show error message"""
        self.console.print(f"[red]✗[/red] {message}")

    def show_warning(self, message: str) -> None:
        """Show warning message"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
