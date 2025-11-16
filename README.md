# News Agent

AI-powered news aggregation agent that collects and analyzes content from GitHub Trending and Hacker News using Claude Agent SDK with MCP integrations.

## Features

- 🤖 **Multi-Provider LLM Support**: Works with Anthropic, OpenAI, OpenRouter, Ollama, Bedrock, Azure, and more via LiteLLM
- 📊 **AI-Powered Analysis**: Relevance scoring, summarization, and intelligent ranking
- 🔄 **Smart Caching**: TTL-based file caching with configurable expiration
- 📝 **Professional Reports**: Markdown reports with rich terminal previews
- ⚙️ **Highly Configurable**: TOML-based configuration with depth control
- 🛡️ **Production-Ready**: Comprehensive error handling, logging, and graceful degradation

## Quick Start

### Installation

```bash
# Using Makefile (recommended)
make install

# Or using pip directly
pip install -e ".[dev]"
```

### Configuration

1. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API key:
# ANTHROPIC_API_KEY=your_key_here
```

2. **Configure sources and preferences** (optional):
```bash
# Edit config.toml to customize:
# - Analysis depth (lightweight/medium/deep)
# - LLM provider and model
# - Ranking strategy (popularity/relevance/balanced)
# - Caching behavior
```

### Basic Usage

```bash
# Run with default settings
news-agent

# Dry run to preview what will be fetched
news-agent --dry-run

# Use deep analysis mode
news-agent --depth deep

# Force fresh data (bypass cache)
news-agent --no-cache

# Custom output location
news-agent --output ./my-report.md

# Enable verbose error logging
news-agent --verbose
```

### Example Output

**Running with default settings:**
```bash
$ news-agent
⏳ Loading configuration...
⏳ Initializing components...
⏳ Running news agent...
⏳ Generating markdown report...
╭────────────────────────────────── Summary ───────────────────────────────────╮
│ GitHub Repos: 0                                                              │
│ HN Posts: 0                                                                  │
│ Analysis Depth: medium                                                       │
│ Report Saved: reports/report-2025-11-15.md                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Report saved to: reports/report-2025-11-15.md
```

**Dry run to preview configuration:**
```bash
$ news-agent --dry-run
⏳ Loading configuration...
⚠ Dry run mode - no data will be fetched
⏳ Would fetch from sources: github, hackernews
```

**Viewing help:**
```bash
$ news-agent --help
Usage: news-agent [OPTIONS]

  Run the news agent to collect and analyze content

Options:
  --config PATH                   Path to configuration file
  --output PATH                   Output file path (default:
                                  reports/report-{date}.md)
  --no-cache                      Force fetch fresh data, ignore cache
  --depth [lightweight|medium|deep]
                                  Analysis depth (overrides config)
  --sources TEXT                  Comma-separated list of sources (e.g.,
                                  github,hn)
  --dry-run                       Show what would be fetched without running
  --verbose                       Enable verbose logging
  --help                          Show this message and exit.
```

> **Note:** The example above shows 0 results because MCP server integrations are pending. Once connected to actual GitHub and Hacker News MCP servers, the reports will contain real trending repositories, developer profiles, and filtered news posts with AI-generated summaries and relevance scores.

## CLI Reference

### Commands

- `news-agent` - Main command to run the news agent

### Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--config PATH` | Path to configuration file | `config.toml` |
| `--output PATH` | Output file path for markdown report | `./reports/report-{date}.md` |
| `--no-cache` | Force fetch fresh data, ignore cache | `False` |
| `--depth LEVEL` | Analysis depth: lightweight, medium, deep | From config |
| `--sources LIST` | Comma-separated sources (github,hn) | All enabled |
| `--dry-run` | Show what would be fetched without running | `False` |
| `--verbose` | Enable verbose error logging | `False` |

### Examples

```bash
# Quick daily update (lightweight analysis, cached)
news-agent --depth lightweight

# Deep research mode (fresh data, comprehensive analysis)
news-agent --depth deep --no-cache

# GitHub only report
news-agent --sources github --output github-trends.md

# Preview before running
news-agent --dry-run --depth deep
```

## Configuration

### config.toml Structure

```toml
[llm]
provider = "anthropic"              # or "openai", "openrouter", "ollama", etc.
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"   # Environment variable name

[analysis]
depth = "medium"                     # lightweight, medium, or deep
top_n = 25                          # Number of top items to return

[sources.github]
enabled = true
mcp_server = "remote"               # Currently stub (pending MCP integration)
categories = ["repositories", "developers"]

[sources.hackernews]
enabled = true
mcp_server = "local"                # Currently stub (pending MCP integration)
endpoints = ["newest", "show"]
filter_topics = ["AI", "ML", "GenAI", "LLM", "machine learning"]

[ranking]
strategy = "balanced"               # popularity, relevance, or balanced

[ranking.weights]
relevance = 0.7                     # Weight for relevance score
popularity = 0.3                    # Weight for popularity score

[caching]
enabled = true
ttl_hours = 1                       # Cache time-to-live

[output]
format = "markdown"
save_path = "./reports"
terminal_preview = true

[retry]
max_attempts = 3
backoff_multiplier = 2
graceful_degradation = true
```

### Analysis Depth Levels

| Level | Summary Length | Token Usage | Use Case |
|-------|---------------|-------------|----------|
| **lightweight** | 1 sentence (50 words) | 128 tokens | Quick daily scans |
| **medium** | 2-3 sentences (100 words) | 256 tokens | Regular monitoring |
| **deep** | 4-5 sentences (200 words) | 512 tokens | In-depth research |

### Ranking Strategies

- **popularity**: Rank by stars/votes only
- **relevance**: Rank by AI relevance score only
- **balanced**: Weighted combination (default: 70% relevance, 30% popularity)

## Development

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_cache_manager.py -v

# Run with coverage
pytest --cov=news_agent tests/
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
mypy src/news_agent
```

### Project Structure

```
news-agent/
├── config.toml              # Main configuration
├── .env                     # API keys (gitignored)
├── src/news_agent/
│   ├── __main__.py         # CLI entry point
│   ├── cli.py              # Click-based CLI
│   ├── agent/              # ReACT agent orchestration
│   ├── analysis/           # Relevance, summarization, ranking
│   ├── cache/              # TTL-based cache manager
│   ├── config/             # TOML loader and Pydantic models
│   ├── llm/                # LiteLLM provider wrapper
│   ├── mcp/                # MCP client stubs (GitHub, HN)
│   ├── output/             # Markdown and terminal output
│   └── utils/              # Retry logic utilities
├── tests/
│   ├── unit/               # Unit tests (43 tests)
│   └── integration/        # Integration tests (pending MCP)
└── docs/plans/             # Design and implementation docs
```

## Current Implementation Status

### ✅ Completed (MVP Ready)

- Project structure and build system
- Configuration system (TOML + Pydantic)
- Multi-provider LLM integration (LiteLLM)
- File-based caching with TTL
- Exponential backoff retry logic
- AI-powered relevance scoring
- Depth-configurable summarization
- Multi-strategy ranking (3 strategies)
- Markdown report generation
- Rich terminal UI with tables
- Complete CLI with all flags
- ReACT agent orchestration

**Test Coverage:** 41/43 tests passing (2 skipped - API-dependent)

### ⏳ Pending (Phase 2)

- **MCP Server Integration**: Connect to actual GitHub and Hacker News MCP servers
- **End-to-End Testing**: With real data sources
- **Social Media Analysis**: Reddit, X.com mention tracking (future enhancement)
- **Scheduling**: Automated daily runs (future enhancement)
- **Email Delivery**: Report distribution (future enhancement)

### Known Limitations

1. **MCP Clients are Stubs**: Currently return empty data until MCP servers are connected
2. **Requires API Key**: Need valid LLM provider API key for analysis features
3. **GitHub/HN Data**: Pending MCP server setup for actual data fetching

## Troubleshooting

### "API key not found" Error

```bash
# Make sure .env file exists and contains your API key
cp .env.example .env
# Edit .env and add:
ANTHROPIC_API_KEY=your_actual_key_here
```

### Empty Results

Currently expected - MCP servers are stubs. Once connected:
- GitHub MCP: https://github.com/github/github-mcp-server
- HN MCP: https://github.com/erithwik/mcp-hn

### Cache Issues

```bash
# Clear cache and fetch fresh data
news-agent --no-cache

# Or manually delete cache directory
rm -rf .cache/news-agent/
```

## Contributing

This project follows strict TDD and uses subagent-driven development:
1. Write tests first
2. Watch them fail
3. Implement to pass
4. Code review before merging

See `docs/plans/` for architecture and implementation details.

## License

[Your License Here]

## Acknowledgments

Built with:
- [Claude](https://claude.ai) - AI assistance
- [LiteLLM](https://github.com/BerriAI/litellm) - Multi-provider LLM integration
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pydantic](https://pydantic.dev/) - Data validation
