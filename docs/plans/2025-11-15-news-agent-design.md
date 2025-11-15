# News Agent Design Document

**Date:** 2025-11-15
**Status:** MVP Planning

## Overview

A CLI-based news aggregation agent that collects, analyzes, and reports on content from multiple sources (GitHub Trending, Hacker News) using a ReACT agent powered by Claude Agent SDK with MCP integrations.

## Goals

**MVP Goals:**
1. Fetch top 25 GitHub trending repositories with analysis (stars, forks, descriptions)
2. Fetch top 25 AI/ML/GenAI-related Hacker News posts with summaries
3. Generate formatted terminal preview and markdown reports
4. Support multiple LLM providers via LiteLLM

**Future Enhancements:**
- Social media mention analysis (Reddit, X.com)
- Scheduled daily execution
- Email report delivery
- Additional data sources

## Technology Stack

- **Language:** Python 3.11+
- **Agent Framework:** Claude Agent SDK
- **LLM Provider:** LiteLLM (supports OpenRouter, Ollama, Bedrock, Azure, GCP)
- **MCP Integrations:**
  - GitHub: Official GitHub MCP server (remote)
  - Hacker News: mcp-hn or similar open-source MCP
- **Configuration:** TOML
- **Output:** Rich (terminal preview) + Markdown (saved reports)

## Architecture

### Agent-Centric Design

The ReACT agent acts as the central orchestrator, coordinating all operations through tool handlers.

```
┌─────────────────────────────────────────────┐
│           news-agent CLI                    │
│         (news-agent run)                    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         ReACT Agent                         │
│    (Claude Agent SDK)                       │
│                                             │
│  - Decides execution strategy               │
│  - Invokes tool handlers                    │
│  - Performs AI analysis                     │
│  - Generates reports                        │
└─────┬───────────────────────────────────┬───┘
      │                                   │
      ▼                                   ▼
┌──────────────────┐            ┌──────────────────┐
│  Tool Handlers   │            │  LiteLLM         │
│                  │            │  Integration     │
│ - GitHub MCP     │            │                  │
│ - HN MCP         │            │ - Relevance      │
│ - Cache Manager  │            │ - Summarization  │
│ - Report Gen     │            │ - Analysis       │
└──────────────────┘            └──────────────────┘
```

### Component Details

#### 1. ReACT Agent (Claude Agent SDK)

**Responsibilities:**
- Load configuration from `config.toml`
- Initialize MCP connections
- Decide execution strategy (parallel/sequential)
- Coordinate tool invocations
- Perform AI-powered analysis
- Generate output

**Tool Handlers:**
- `fetch_github_trending`: Retrieves trending repos/developers via GitHub MCP
- `fetch_hn_content`: Retrieves posts/comments via HN MCP
- `analyze_relevance`: Scores content relevance using LLM
- `rank_results`: Ranks items based on configurable strategy
- `generate_report`: Creates markdown report

#### 2. MCP Integration Layer

**GitHub MCP (Remote):**
- Source: https://github.com/github/github-mcp-server
- Endpoints: /trending, /trending/developers
- Returns: Repo metadata (stars, forks, description, links)

**Hacker News MCP:**
- Source: https://github.com/erithwik/mcp-hn or custom
- Endpoints: /newest, /show
- Returns: Posts, comments, votes, metadata

#### 3. LLM Provider (LiteLLM)

**Use Cases:**
- **Relevance Scoring:** Evaluate HN posts for AI/ML/GenAI relevance
- **Summarization:** Generate article and comment summaries
- **Analysis:** Analyze GitHub project popularity trends
- **Ranking:** Intelligent ranking based on multiple signals

**Configurable Depth:**
- `lightweight`: Basic stats + one-line summaries
- `medium`: Statistical analysis + coherent summaries
- `deep`: Trend analysis, sentiment, community insights

#### 4. Caching Strategy

**Smart Caching:**
- Cache raw data from MCP servers (time-based TTL)
- Regenerate analysis on demand (allows depth changes without re-fetch)
- `--no-cache` flag to force fresh data
- Cache location: `.cache/news-agent/`

#### 5. Configuration (TOML)

**Structure:**
```toml
[llm]
provider = "openrouter"  # or "ollama", "bedrock", "azure", etc.
model = "anthropic/claude-3-5-sonnet"
api_key_env = "OPENROUTER_API_KEY"

[analysis]
depth = "medium"  # lightweight, medium, deep
top_n = 25

[sources.github]
enabled = true
mcp_server = "https://github-mcp.example.com"
categories = ["repositories", "developers"]

[sources.hackernews]
enabled = true
mcp_server = "local"  # or remote URL
endpoints = ["/newest", "/show"]
filter_topics = ["AI", "ML", "GenAI", "LLM"]

[ranking]
strategy = "balanced"  # popularity, relevance, balanced
weights = { relevance = 0.7, popularity = 0.3 }

[caching]
enabled = true
ttl_hours = 1

[output]
format = "markdown"
save_path = "./reports"
terminal_preview = true

[retry]
max_attempts = 3
backoff_multiplier = 2
graceful_degradation = true
```

#### 6. Error Handling

**Strategy:**
- Configurable retry with exponential backoff
- Graceful degradation (continue with partial results)
- Detailed error logging
- User-friendly error messages

**Scenarios:**
- Network failures → Retry with backoff
- Rate limits → Wait and retry, use cache if available
- MCP server unavailable → Skip source, report in output
- Parsing errors → Log and continue with other items

#### 7. Output Format

**Terminal Preview:**
- Rich formatted tables with colors
- Progress indicators during fetching
- Summary statistics
- Preview of top items

**Markdown Report:**
```markdown
# News Agent Report
Generated: 2025-11-15 10:30 AM

## GitHub Trending Repositories (Top 25)

### 1. [owner/repo-name](https://github.com/owner/repo)
**Description:** Brief description...
**Stats:** ⭐ 1.2k stars | 🔱 234 forks | 📈 +150 stars this week
**Analysis:** [AI-generated analysis of project popularity and trend]

---

## Hacker News - AI/ML/GenAI Topics (Top 25)

### 1. [Article Title](https://news.ycombinator.com/item?id=12345)
**Link:** https://example.com/article
**Votes:** 234 points | 56 comments
**Summary:** [AI-generated article summary]
**Discussion Highlights:** [AI-generated summary of key comment themes]

---

## Summary
- GitHub: 25 trending repositories analyzed
- Hacker News: 25 AI/ML topics curated from 150 posts
- Analysis depth: medium
- Sources: GitHub MCP, HN MCP
```

## CLI Interface

**Primary Command:**
```bash
news-agent run [OPTIONS]
```

**Options:**
- `--config PATH`: Path to config file (default: `config.toml`)
- `--output PATH`: Output file path (default: `./reports/report-{date}.md`)
- `--no-cache`: Force fetch fresh data
- `--depth {lightweight,medium,deep}`: Analysis depth override
- `--sources SOURCE[,SOURCE]`: Run specific sources only (e.g., `github`, `hn`)
- `--dry-run`: Show what would be fetched without running
- `--verbose`: Detailed logging

**Examples:**
```bash
# Standard run
news-agent run

# Deep analysis with fresh data
news-agent run --depth deep --no-cache

# GitHub only, custom output
news-agent run --sources github --output ./github-report.md

# Verbose logging
news-agent run --verbose
```

## Project Structure

```
news-agent/
├── config.toml                 # Main configuration
├── .env                        # API keys (gitignored)
├── pyproject.toml             # Python project config
├── README.md
├── docs/
│   └── plans/
│       └── 2025-11-15-news-agent-design.md
├── src/
│   └── news_agent/
│       ├── __init__.py
│       ├── __main__.py        # CLI entry point
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── react_agent.py # ReACT agent implementation
│       │   └── tools.py       # Tool handler definitions
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── github_client.py
│       │   └── hn_client.py
│       ├── llm/
│       │   ├── __init__.py
│       │   └── provider.py    # LiteLLM integration
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── relevance.py   # Relevance scoring
│       │   ├── ranking.py     # Ranking logic
│       │   └── summarization.py
│       ├── cache/
│       │   ├── __init__.py
│       │   └── manager.py     # Cache management
│       ├── output/
│       │   ├── __init__.py
│       │   ├── terminal.py    # Rich terminal output
│       │   └── markdown.py    # Markdown generation
│       ├── config/
│       │   ├── __init__.py
│       │   └── loader.py      # TOML config loader
│       └── utils/
│           ├── __init__.py
│           ├── retry.py       # Retry logic
│           └── logger.py      # Logging setup
├── tests/
│   └── ...
├── .cache/                    # Local cache (gitignored)
└── reports/                   # Generated reports (gitignored)
```

## Implementation Phases

### Phase 1: Foundation (MVP Core)
- Set up Python project structure
- Implement TOML config loader
- Set up LiteLLM integration
- Basic CLI with argument parsing

### Phase 2: MCP Integration
- Integrate GitHub MCP server (remote)
- Integrate/modify mcp-hn for Hacker News
- Implement tool handlers for agent
- Basic data fetching and parsing

### Phase 3: ReACT Agent
- Implement Claude Agent SDK integration
- Create tool handler registry
- Implement execution strategy logic
- Basic agent orchestration

### Phase 4: Analysis & Ranking
- AI-powered relevance scoring
- Summarization pipeline
- Configurable ranking strategies
- Depth-based analysis levels

### Phase 5: Output & Caching
- Rich terminal preview
- Markdown report generation
- Smart caching implementation
- Error handling and retries

### Phase 6: Polish & Testing
- Comprehensive error handling
- Unit and integration tests
- Documentation
- CLI refinements

### Future: Enhancements
- Social media analysis (Reddit, X.com)
- Scheduling (cron/systemd integration)
- Email delivery
- Web dashboard
- Additional data sources

## Success Criteria

**MVP is complete when:**
1. ✅ Can fetch GitHub trending repos via MCP
2. ✅ Can fetch HN posts via MCP
3. ✅ AI filters HN content for AI/ML/GenAI relevance
4. ✅ Generates top 25 ranked results from each source
5. ✅ Displays rich terminal preview
6. ✅ Saves markdown report to file
7. ✅ Supports multiple LLM providers via LiteLLM
8. ✅ Configurable via TOML
9. ✅ Handles errors gracefully with retry logic
10. ✅ Smart caching with override flag

## Notes

- API keys provided via environment variables (`.env`)
- GitHub MCP server is remotely hosted (no local setup required)
- HN MCP may need custom modifications or local hosting
- Social media analysis deferred to post-MVP
- Email delivery deferred to post-MVP
- Scheduling deferred to post-MVP
