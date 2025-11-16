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
    from datetime import datetime
    import sys
    import logging

    # Load environment variables
    load_dotenv()

    # Configure logging based on verbose flag
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',  # Simple format for clean output
            force=True  # Override any existing configuration
        )
    else:
        logging.basicConfig(level=logging.WARNING, force=True)

    from news_agent.config.loader import load_config
    from news_agent.config.models import AnalysisConfig
    from news_agent.llm.provider import LLMProvider
    from news_agent.cache.manager import CacheManager
    from news_agent.mcp.github_client import GitHubMCPClient
    from news_agent.mcp.hn_client import HackerNewsMCPClient
    from news_agent.analysis.relevance import RelevanceScorer
    from news_agent.analysis.ranking import Ranker
    from news_agent.agent.tools import ToolRegistry
    from news_agent.agent.react_agent import NewsAgent
    from news_agent.output.terminal import TerminalDisplay
    from news_agent.output.markdown import MarkdownGenerator

    display = TerminalDisplay()

    try:
        # Load configuration
        display.show_progress("Loading configuration...")
        cfg = load_config(config)

        # Apply overrides
        if depth:
            cfg.analysis.depth = depth  # type: ignore

        if dry_run:
            display.show_warning("Dry run mode - no data will be fetched")
            display.show_progress(f"Would fetch from sources: {', '.join(s for s in ['github', 'hackernews'] if getattr(cfg.sources, s.replace('hackernews', 'hackernews')).enabled)}")
            return

        # Initialize components
        display.show_progress("Initializing components...")

        llm_provider = LLMProvider(cfg.llm)
        cache_manager = CacheManager(Path(".cache/news-agent"), cfg.caching)

        if no_cache:
            display.show_progress("Clearing cache (--no-cache flag)")
            cache_manager.clear()

        github_client = GitHubMCPClient(cfg.sources.github)
        hn_client = HackerNewsMCPClient(cfg.sources.hackernews)

        relevance_scorer = RelevanceScorer(llm_provider, cfg.analysis)
        ranker = Ranker(cfg.ranking)

        tool_registry = ToolRegistry(
            github_client,
            hn_client,
            relevance_scorer,
            ranker,
            cache_manager
        )

        # Create agent
        agent = NewsAgent(cfg, tool_registry, llm_provider)

        # Run agent
        display.show_progress("Running news agent...")
        results = agent.run(no_cache=no_cache)

        # Display preview
        if cfg.output.terminal_preview:
            if results["github_repos"]:
                display.show_github_preview(results["github_repos"])

            if results["hn_posts"]:
                display.show_hn_preview(results["hn_posts"])

        # Generate markdown report
        display.show_progress("Generating markdown report...")
        markdown_gen = MarkdownGenerator()
        report_content = markdown_gen.generate_report(results)

        # Determine output path
        if output:
            output_path = output
        else:
            reports_dir = Path(cfg.output.save_path)
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d")
            output_path = reports_dir / f"report-{timestamp}.md"

        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content)

        # Show summary
        display.show_summary({
            "github_count": len(results["github_repos"]),
            "hn_count": len(results["hn_posts"]),
            "depth": cfg.analysis.depth,
            "report_path": str(output_path)
        })

        display.show_success(f"Report saved to: {output_path}")

    except Exception as e:
        display.show_error(f"Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Entry point for CLI"""
    run()
