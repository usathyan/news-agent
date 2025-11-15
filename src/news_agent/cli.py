from pathlib import Path
from typing import Optional
import click
from dotenv import load_dotenv


@click.command()
@click.option(
    '--config',
    type=click.Path(exists=True, path_type=Path),
    default='config.toml',
    help='Path to configuration file'
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    default=None,
    help='Output file path (default: reports/report-{date}.md)'
)
@click.option(
    '--no-cache',
    is_flag=True,
    help='Force fetch fresh data, ignore cache'
)
@click.option(
    '--depth',
    type=click.Choice(['lightweight', 'medium', 'deep']),
    default=None,
    help='Analysis depth (overrides config)'
)
@click.option(
    '--sources',
    type=str,
    default=None,
    help='Comma-separated list of sources (e.g., github,hn)'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be fetched without running'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose logging'
)
def run(
    config: Path,
    output: Optional[Path],
    no_cache: bool,
    depth: Optional[str],
    sources: Optional[str],
    dry_run: bool,
    verbose: bool
) -> None:
    """Run the news agent to collect and analyze content"""
    # Load environment variables
    load_dotenv()

    from news_agent.output.terminal import TerminalDisplay

    display = TerminalDisplay()
    display.show_progress("Loading configuration...")

    # TODO: Implement agent orchestration
    # This will be implemented in Task 14 (Agent Integration)

    if dry_run:
        display.show_warning("Dry run mode - no data will be fetched")
        display.show_progress("Would fetch from sources: github, hackernews")
        return

    display.show_error("Agent implementation pending (Task 14)")


def main() -> None:
    """Entry point for CLI"""
    run()
