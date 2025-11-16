# News Agent

AI-powered news aggregation that automatically collects trending content from GitHub and Hacker News, analyzes it with AI, and generates daily reports.

## What It Does

Runs an AI agent that:
- Fetches today's trending GitHub repositories
- Collects relevant AI/ML posts from Hacker News
- Uses Claude to analyze and score relevance
- Generates a beautiful markdown report with ranked results
- Caches results so you're not fetching constantly

Perfect for staying updated on tech trends without manually checking multiple sources.

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
# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_key_here (or OPENROUTER_API_KEY, etc.)
# GITHUB_PAT=your_github_token (optional - for higher rate limits)
# LANGSMITH_API_KEY=your_langsmith_key (optional - for telemetry)
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
                          GitHub Trending Repositories
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Rank   ┃ Repository               ┃ Stars ┃ Forks ┃ Description              ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1      │ raduacg/game-mechanics-… │   153 │    11 │ A list of 171 game       │
│        │                          │       │       │ mechanics techniques...  │
│ 2      │ SouzaFrontend/tisa       │   142 │     0 │ tisa is an emulator for  │
│        │                          │       │       │ the Tiny ISA             │
│ 3      │ hanakim3945/bl_sbx       │    63 │     8 │ itunesstored & bookassetd│
│        │                          │       │       │ sbx escape               │
└────────┴──────────────────────────┴───────┴───────┴──────────────────────────┘
                        Hacker News - AI/ML/GenAI Topics
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Rank   ┃ Title                                            ┃ Score ┃ Comments ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ 1      │ Solving a Million-Step LLM Task with Zero Errors │     2 │        0 │
│ 2      │ Show HN: Gerbil – Open source desktop app for    │    36 │        0 │
│        │ running LLMs...                                  │       │          │
│ 3      │ Show HN: Tiny Diffusion – Character-level text   │   154 │        0 │
│        │ diffusion m...                                   │       │          │
└────────┴──────────────────────────────────────────────────┴───────┴──────────┘
⏳ Generating markdown report...
╭────────────────────────────────── Summary ───────────────────────────────────╮
│ GitHub Repos: 6                                                              │
│ HN Posts: 10                                                                 │
│ Analysis Depth: medium                                                       │
│ Report Saved: reports/report-2025-11-15.md                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Report saved to: reports/report-2025-11-15.md
```

**Real data from generated report:**
- **GitHub**: 6 trending repositories (game mechanics, emulators, iOS exploits, UI libraries)
- **Hacker News**: 10 AI/ML posts filtered by topic (LLM tools, diffusion models, AI systems)
- **AI Analysis**: Relevance scoring and filtering applied
- **Format**: Rich terminal tables + markdown report

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

[telemetry]
enabled = true                      # Enable/disable telemetry
backend = "langsmith"               # langsmith, otel, or langfuse
project_name = "news-agent"         # Project name in telemetry backend
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

### Telemetry & Observability

The news agent includes built-in LangSmith integration for full observability of agent execution and LLM calls.

**Automatic Tracing Setup:**
```bash
# Simply add your LangSmith API key to .env
LANGSMITH_API_KEY=your_api_key_here

# Run the agent - tracing happens automatically
news-agent --verbose
```

**What's Traced:**
- **Agent Execution**: Main workflow trace (`news_agent_run`)
  - GitHub data collection phase
  - Hacker News data collection phase
  - Relevance scoring phase
  - Ranking phase
- **LLM Calls**: Individual prompt/completion calls
  - Relevance scoring prompts
  - Token usage and costs
  - API latency and response times
- **Data Flow**: Complete execution hierarchy from agent to LLM calls

**Trace Types Recorded:**

1. **Root Trace**: `news_agent_run`
   - Captures the entire agent execution
   - Shows overall execution time and status
   - Parent trace for all child spans

2. **Phase Traces**: `collect_github_data`, `collect_hn_data`
   - Data collection spans
   - API call details
   - Data transformation steps

3. **LLM Traces**: LiteLLM wrapped completions
   - Prompt text and parameters
   - Token counts (input/output/total)
   - Model and provider used
   - Response latency

**Viewing Traces:**
```bash
# Open LangSmith dashboard (one-click)
make langsmith

# Or visit: https://smith.langchain.com/
# Then navigate to project: "news-agent"
```

**Example Trace Structure in LangSmith:**
```
news_agent_run (Root)
├── collect_github_data
│   ├── GitHub API call
│   └── Data processing
├── collect_hn_data
│   ├── HN API call (multiple posts)
│   └── Data aggregation
├── score_relevance (Relevance Scoring)
│   └── llm_complete (7 LLM calls for batch scoring)
│       ├── Call 1: Score batch of 5 posts
│       ├── Call 2: Score batch of 5 posts
│       └── Call 3: Score batch of 5 posts
└── rank_items (Ranking)
```

**Configuration:**
- Automatic: Set `LANGSMITH_API_KEY` in `.env` - tracing enables automatically
- Project: Traces appear in "news-agent" project (configurable via `LANGSMITH_PROJECT`)
- Optional: Set `telemetry.enabled = false` in `config.toml` to disable

**Benefits:**
- 🔍 **Debug LLM responses**: See exact prompts and responses in traces
- 💰 **Track costs**: Monitor token usage by operation
- ⏱️ **Performance analysis**: Identify bottlenecks and slow operations
- 📊 **Relevance tuning**: Understand how AI scoring decisions are made
- 🔄 **Workflow visibility**: See complete execution flow and dependencies


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

## Need Help?

**For developers**: See `docs/DEVELOPER_NOTES.md` for architecture, how it works, and how to contribute.

## License

MIT License - see [LICENSE](LICENSE) file for details

Copyright (c) 2025 Umesh Bhatt

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## Acknowledgments

Built with:
- [Claude](https://claude.ai) - AI assistance
- [LiteLLM](https://github.com/BerriAI/litellm) - Multi-provider LLM integration
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pydantic](https://pydantic.dev/) - Data validation
