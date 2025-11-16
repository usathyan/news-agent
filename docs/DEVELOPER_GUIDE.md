# News Agent - Developer Guide

A comprehensive guide to understanding the news-agent architecture, implementation, and LangSmith telemetry integration.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Design](#system-design)
3. [Code Organization](#code-organization)
4. [Execution Flow](#execution-flow)
5. [LangSmith Telemetry Implementation](#langsmith-telemetry-implementation)
6. [Tracing in Detail](#tracing-in-detail)
7. [Key Components](#key-components)
8. [Data Flow](#data-flow)
9. [Development Patterns](#development-patterns)

---

## Architecture Overview

The news agent is a multi-component system that orchestrates data collection, AI analysis, and reporting:

```mermaid
graph TB
    subgraph "User Interface"
        CLI["Click CLI<br/>news-agent command"]
    end

    subgraph "Configuration"
        Config["TOML Config<br/>config.toml"]
        EnvVars["Environment<br/>Variables"]
    end

    subgraph "Core Agent"
        Agent["NewsAgent<br/>ReACT Orchestration"]
        ToolRegistry["Tool Registry<br/>GitHub, HN Tools"]
    end

    subgraph "Data Collection"
        GHClient["GitHub Client<br/>REST API"]
        HNClient["HN Client<br/>Firebase API"]
        Cache["Cache Manager<br/>TTL-based"]
    end

    subgraph "Analysis & Processing"
        Scorer["Relevance Scorer<br/>LLM-based"]
        Ranker["Ranker<br/>Multi-strategy"]
        Summarizer["Summarizer<br/>Depth-configurable"]
    end

    subgraph "LLM & Telemetry"
        LLM["LiteLLM Provider<br/>Multi-provider"]
        LangSmith["LangSmith<br/>Observability"]
    end

    subgraph "Output"
        MarkdownGen["Markdown Generator"]
        TerminalUI["Terminal Display<br/>Rich Tables"]
    end

    CLI --> Config
    CLI --> EnvVars
    Config --> Agent
    EnvVars --> Agent
    Agent --> ToolRegistry
    ToolRegistry --> GHClient
    ToolRegistry --> HNClient
    GHClient --> Cache
    HNClient --> Cache
    Agent --> Scorer
    Agent --> Ranker
    Agent --> Summarizer
    Scorer --> LLM
    LLM --> LangSmith
    MarkdownGen --> LLM
    Agent --> MarkdownGen
    Agent --> TerminalUI
```

---

## System Design

### Component Interaction Diagram

```mermaid
graph LR
    A["CLI<br/>Entry Point"]
    B["Config<br/>Loader"]
    C["LLM Provider<br/>Initialization"]
    D["NewsAgent<br/>Main Loop"]
    E["Tool Registry"]
    F["Analysis<br/>Pipeline"]
    G["Report<br/>Generator"]
    H["LangSmith<br/>Tracing"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> D
    D --> G
    C -.->|All LLM calls| H
    F -.->|All operations| H
    D -.->|Main workflow| H
```

### Data Flow Architecture

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Config
    participant Agent
    participant GitHub
    participant HackerNews
    participant LLM
    participant Analyzer
    participant LangSmith

    User->>CLI: news-agent --verbose
    CLI->>Config: Load config.toml
    CLI->>Agent: Initialize with config

    Agent->>GitHub: Fetch trending repos
    GitHub-->>Agent: 25 repositories
    Agent->>LangSmith: Record API call

    Agent->>HackerNews: Fetch posts
    HackerNews-->>Agent: 30 posts
    Agent->>LangSmith: Record API call

    Agent->>LLM: Score relevance (batches)
    LLM-->>Agent: Relevance scores
    Agent->>LangSmith: Record LLM calls (7 calls)

    Agent->>Analyzer: Rank items
    Analyzer-->>Agent: Ranked results

    Agent->>LLM: Generate report
    LLM-->>Agent: Final report
    Agent->>LangSmith: Record report generation

    Agent-->>User: Report output
    User->>LangSmith: View traces in dashboard
```

---

## Code Organization

### Directory Structure

```
news-agent/
├── src/news_agent/
│   ├── __main__.py              # Package entry point
│   ├── cli.py                   # Click CLI commands
│   │                             # ├─ Loads env vars
│   │                             # ├─ Enables LangSmith tracing
│   │                             # └─ Orchestrates execution
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── react_agent.py       # NewsAgent (main orchestrator)
│   │   │                         # ├─ collect_github_data()
│   │   │                         # ├─ collect_hn_data()
│   │   │                         # └─ run() [root trace]
│   │   └── tools.py             # Tool registry & implementations
│   │
│   ├── llm/
│   │   └── provider.py          # LiteLLM wrapper
│   │                             # └─ complete() [LLM trace]
│   │
│   ├── analysis/
│   │   ├── relevance.py         # Relevance scoring (LLM-based)
│   │   ├── ranking.py           # Multi-strategy ranking
│   │   └── summarizer.py        # Configurable summarization
│   │
│   ├── mcp/
│   │   ├── github_client.py     # GitHub REST API client
│   │   └── hn_client.py         # Hacker News API client
│   │
│   ├── cache/
│   │   └── manager.py           # TTL-based file cache
│   │
│   ├── config/
│   │   ├── loader.py            # TOML config parsing
│   │   └── models.py            # Pydantic config models
│   │
│   ├── output/
│   │   ├── markdown.py          # Markdown report generation
│   │   └── terminal.py          # Rich terminal UI
│   │
│   └── utils/
│       └── retry.py             # Exponential backoff retry logic
│
├── tests/
│   ├── unit/                    # Unit tests (43 tests)
│   └── integration/             # Integration tests
│
├── docs/
│   ├── DEVELOPER_GUIDE.md       # This file
│   └── plans/                   # Architecture & design docs
│
├── config.toml                  # Configuration file
├── .env.example                 # Environment template
├── test_langsmith_tracing.py    # Minimal tracing test
└── Makefile                     # Development targets
```

---

## Execution Flow

### Main Execution Pipeline

```mermaid
graph TD
    Start["CLI Entry<br/>news-agent --verbose"]

    subgraph "Initialization"
        LoadEnv["Load .env<br/>os.environ"]
        EnableTrace["Enable LangSmith<br/>LANGSMITH_TRACING=true<br/>(if API key present)"]
        LoadConfig["Load config.toml<br/>Pydantic validation"]
        InitLLM["Initialize LLMProvider<br/>Multi-provider setup"]
    end

    subgraph "Main Execution (Traced)"
        RunAgent["agent.run()<br/>@traceable"]

        subgraph "Phase 1: Data Collection"
            CollectGH["_collect_github_data<br/>@traceable"]
            GHAPICall["GitHub API<br/>Fetch trending"]
            GHCache["Check cache<br/>TTL validation"]
        end

        subgraph "Phase 2: Hacker News"
            CollectHN["_collect_hn_data<br/>@traceable"]
            HNAPICall["HN API<br/>Fetch posts"]
            HNCache["Check cache<br/>TTL validation"]
        end

        subgraph "Phase 3: Analysis"
            ScoreRel["score_relevance()<br/>LLM calls"]
            BatchScore["Batch scoring<br/>5 posts per call"]
            FilterRel["Filter by threshold<br/>score > 0.5"]
        end

        subgraph "Phase 4: Ranking"
            RankItems["rank_items()<br/>Apply strategy"]
            ApplyWeights["Apply weights<br/>70% relevance<br/>30% popularity"]
            TopN["Select top N<br/>From config"]
        end

        subgraph "Phase 5: Output"
            GenReport["Generate report<br/>Markdown & Terminal"]
            Terminal["Display tables<br/>Rich UI"]
            SaveFile["Save markdown<br/>reports/report-*.md"]
        end
    end

    subgraph "Telemetry (LangSmith)"
        Traces["All operations traced"]
        Dashboard["View in dashboard<br/>smith.langchain.com"]
    end

    Start --> LoadEnv
    LoadEnv --> EnableTrace
    EnableTrace --> LoadConfig
    LoadConfig --> InitLLM
    InitLLM --> RunAgent

    RunAgent --> CollectGH
    CollectGH --> GHCache
    GHCache --> GHAPICall

    RunAgent --> CollectHN
    CollectHN --> HNCache
    HNCache --> HNAPICall

    RunAgent --> ScoreRel
    ScoreRel --> BatchScore
    BatchScore --> FilterRel

    RunAgent --> RankItems
    RankItems --> ApplyWeights
    ApplyWeights --> TopN

    RunAgent --> GenReport
    GenReport --> Terminal
    GenReport --> SaveFile

    RunAgent -.-> Traces
    ScoreRel -.-> Traces
    GHAPICall -.-> Traces
    HNAPICall -.-> Traces

    Traces --> Dashboard
```

### Detailed: Relevance Scoring Flow

```mermaid
graph TD
    A["Input: 29 posts"]
    B["Group into batches<br/>5 posts per batch"]
    C["Batch 1: Posts 1-5"]
    D["Batch 2: Posts 6-10"]
    E["Batch 3: Posts 11-15"]
    F["Batch 4: Posts 16-20"]
    G["Batch 5: Posts 21-25"]
    H["Batch 6: Posts 26-29"]

    I["Call LLM<br/>Complete prompt"]
    J["Parse JSON response"]
    K["Extract scores"]
    L["Merge results"]
    M["Output: All 29 posts<br/>with scores"]
    N["Filter: score > 0.5"]
    O["Result: 16 posts"]

    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H

    C --> I
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
```

---

## LangSmith Telemetry Implementation

### How Tracing is Enabled

#### 1. CLI Initialization (`src/news_agent/cli.py`)

```python
def run(config: Path, verbose: bool, ...):
    # Load environment variables
    load_dotenv()

    # Enable LangSmith tracing if API key is configured
    if os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGSMITH_TRACING"] = "true"

    # ... rest of initialization
```

**Why this works:**
- `LANGSMITH_TRACING=true` is the official LangSmith environment variable
- When set, LangSmith SDK automatically:
  - Creates trace context for all `@traceable` decorated functions
  - Records all LLM calls via LiteLLM callbacks
  - Persists traces to the configured project

#### 2. Agent Decoration (`src/news_agent/agent/react_agent.py`)

```python
from langsmith import traceable

class NewsAgent:
    @traceable(name="news_agent_run")
    def run(self, no_cache: bool = False) -> dict[str, Any]:
        """Root trace for entire agent execution"""
        # ... main workflow

    @traceable(name="collect_github_data")
    def _collect_github_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """GitHub collection phase"""
        # ... GitHub collection logic

    @traceable(name="collect_hn_data")
    def _collect_hn_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """Hacker News collection phase"""
        # ... HN collection logic
```

**Trace Names:**
- `news_agent_run` - Root trace, captures entire execution
- `collect_github_data` - GitHub API phase
- `collect_hn_data` - Hacker News API phase

#### 3. LLM Integration (`src/news_agent/llm/provider.py`)

```python
from langsmith import traceable

class LLMProvider:
    @traceable(name="llm_complete")
    def complete(self, messages: List[Dict[str, Any]], ...) -> str:
        """LLM completion with automatic tracing"""
        response = completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self._api_key,
            **kwargs
        )
        return response.choices[0].message.content
```

**Why this works:**
- LiteLLM detects active LangSmith trace context
- Automatically sends completion details to LangSmith via callback
- Includes: prompt, response, tokens, model, latency

---

## Tracing in Detail

### Trace Hierarchy

```mermaid
graph TD
    Root["news_agent_run<br/>Root Trace<br/>Duration: ~45s<br/>Status: Success"]

    GH["collect_github_data<br/>Span<br/>Duration: ~1s<br/>Data: 25 repos"]
    HN["collect_hn_data<br/>Span<br/>Duration: ~2s<br/>Data: 29 posts"]
    Score["score_relevance<br/>Span<br/>Duration: ~30s<br/>Operations: 6 LLM calls"]
    Rank["rank_items<br/>Span<br/>Duration: ~1s"]
    Report["Generate Report<br/>Span<br/>Duration: ~2s"]

    LLM1["llm_complete #1<br/>Batch 1-5 posts<br/>Tokens: 484"]
    LLM2["llm_complete #2<br/>Batch 6-10 posts<br/>Tokens: 408"]
    LLM3["llm_complete #3<br/>Batch 11-15 posts<br/>Tokens: 525"]
    LLM4["llm_complete #4<br/>Batch 16-20 posts<br/>Tokens: 470"]
    LLM5["llm_complete #5<br/>Batch 21-25 posts<br/>Tokens: 479"]
    LLM6["llm_complete #6<br/>Batch 26-29 posts<br/>Tokens: 451"]

    Root --> GH
    Root --> HN
    Root --> Score
    Root --> Rank
    Root --> Report

    Score --> LLM1
    Score --> LLM2
    Score --> LLM3
    Score --> LLM4
    Score --> LLM5
    Score --> LLM6
```

### Trace Content for Each Span

#### Root Trace: `news_agent_run`

```json
{
  "name": "news_agent_run",
  "status": "success",
  "start_time": "2025-11-16T10:19:28Z",
  "end_time": "2025-11-16T10:21:13Z",
  "duration_ms": 105000,
  "inputs": {
    "no_cache": false
  },
  "outputs": {
    "github_repos": 25,
    "hn_posts": 16,
    "sources": ["github", "hackernews"]
  }
}
```

#### Phase Trace: `collect_github_data`

```json
{
  "name": "collect_github_data",
  "status": "success",
  "duration_ms": 1240,
  "inputs": {
    "no_cache": false
  },
  "outputs": {
    "count": 25,
    "data": [
      {
        "name": "repo-name",
        "stars": 153,
        "description": "Repository description"
      }
    ]
  }
}
```

#### LLM Call Trace: `llm_complete`

```json
{
  "name": "llm_complete",
  "status": "success",
  "duration_ms": 4500,
  "inputs": {
    "messages": [
      {
        "role": "system",
        "content": "Score relevance of posts..."
      },
      {
        "role": "user",
        "content": "Posts: 1. Post Title...\n2. Post Title..."
      }
    ],
    "model": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7,
    "max_tokens": 1024
  },
  "outputs": {
    "response": "{\"scores\": [0.8, 0.9, 0.7, ...]}"
  },
  "metadata": {
    "tokens_used": {
      "prompt": 267,
      "completion": 217,
      "total": 484
    },
    "model": "claude-3.5-sonnet",
    "provider": "openrouter",
    "latency_ms": 4500
  }
}
```

---

## Key Components

### 1. NewsAgent (`src/news_agent/agent/react_agent.py`)

The main orchestrator using ReACT (Reasoning + Acting) pattern:

```mermaid
graph LR
    Think["Reason<br/>Plan workflow"]
    Act["Act<br/>Execute operations"]
    Obs["Observe<br/>Get results"]
    Think --> Act
    Act --> Obs
    Obs --> Think
```

**Key Methods:**
- `run()` - Main execution loop (traced)
- `_collect_github_data()` - GitHub data collection (traced)
- `_collect_hn_data()` - HN data collection (traced)
- Uses `ToolRegistry` to call specialized tools

### 2. LLMProvider (`src/news_agent/llm/provider.py`)

Multi-provider LLM wrapper using LiteLLM:

```python
class LLMProvider:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model
        # Validates provider
        # Loads API key
        # Configures LangSmith if available

    @traceable(name="llm_complete")
    def complete(self, messages, temperature, max_tokens, **kwargs) -> str:
        """Single LLM completion with tracing"""
        # Calls LiteLLM
        # Validates response
        # Logs token usage
        # Returns response text
```

**Providers Supported:**
- Anthropic (Claude)
- OpenAI (GPT)
- OpenRouter (Multi-model)
- Azure, Bedrock, Cohere, Ollama

### 3. Data Clients

#### GitHub Client (`src/news_agent/mcp/github_client.py`)

```python
def fetch_trending_repos(self, no_cache: bool) -> dict:
    """
    Fetches trending repositories using GitHub Search API

    Query: created:>{date} stars:>50
    Returns: Up to 25 repositories sorted by stars
    """
```

#### Hacker News Client (`src/news_agent/mcp/hn_client.py`)

```python
def fetch_posts(self, endpoint: str, no_cache: bool) -> dict:
    """
    Fetches HN posts via Firebase API

    Endpoints: "newest", "show" (Show HN posts)
    Uses parallel fetching: asyncio.gather() for ~10x speedup
    """
```

### 4. Relevance Scorer (`src/news_agent/analysis/relevance.py`)

Uses LLM to score posts for relevance to configured topics:

```python
def score(self, items: List[dict], topics: List[str]) -> List[dict]:
    """
    Scores items for relevance using LLM

    Process:
    1. Batch items (5 per batch)
    2. Create scoring prompt with topics
    3. Call LLM for each batch
    4. Parse JSON responses
    5. Merge results
    6. Filter by threshold (> 0.5)

    Returns items with relevance_score field
    """
```

### 5. Ranker (`src/news_agent/analysis/ranking.py`)

Multi-strategy ranking system:

```mermaid
graph TD
    Items["Input Items"]
    Strategy["Ranking Strategy"]

    subgraph Strategies
        Pop["Popularity<br/>Sort by stars/votes"]
        Rel["Relevance<br/>Sort by AI score"]
        Bal["Balanced<br/>Weighted combination<br/>70% relevance<br/>30% popularity"]
    end

    Strategy -->|popularity| Pop
    Strategy -->|relevance| Rel
    Strategy -->|balanced| Bal

    Pop --> Sort["Sort items"]
    Rel --> Sort
    Bal --> Sort

    Sort --> TopN["Select top N<br/>From config"]
    TopN --> Output["Output: Ranked items"]
```

---

## Data Flow

### GitHub Collection Flow

```mermaid
graph TD
    A["Config: categories<br/>['repositories']"]
    B["Check cache<br/>.cache/news-agent/"]
    C{"Cache<br/>valid?"}
    D["Return cached<br/>data"]
    E["Query GitHub API<br/>created:>2025-11-15<br/>stars:>50"]
    F["Parse results<br/>Extract: name, stars,<br/>forks, description"]
    G["Cache results<br/>TTL: 1 hour"]
    H["Return: 25 repos"]

    A --> B
    B --> C
    C -->|Yes| D
    C -->|No| E
    E --> F
    F --> G
    G --> H
    D --> H
```

### Hacker News Collection Flow

```mermaid
graph TD
    A["Config: endpoints<br/>['newest', 'show']"]
    B["For each endpoint"]
    C["Check cache"]
    D{"Cache<br/>valid?"}
    E["Return cached"]
    F["Fetch posts<br/>ID list"]
    G["Parallel fetch<br/>asyncio.gather"]
    H["Get 30-50 items"]
    I["Transform data<br/>Extract: title,<br/>score, comments"]
    J["Cache results<br/>TTL: 1 hour"]
    K["Merge all<br/>29 posts"]

    A --> B
    B --> C
    C --> D
    D -->|Yes| E
    D -->|No| F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    E --> K
```

---

## Development Patterns

### 1. Test-Driven Development (TDD)

All features follow RED-GREEN-REFACTOR cycle:

```mermaid
graph LR
    Write["Write failing<br/>test"]
    Run["Run test<br/>RED"]
    Implement["Implement<br/>minimal code"]
    Pass["Test passes<br/>GREEN"]
    Refactor["Refactor<br/>REFACTOR"]

    Write --> Run
    Run --> Implement
    Implement --> Pass
    Pass --> Refactor
    Refactor --> Write
```

### 2. Code Organization Pattern

```
Feature Implementation:
├── Write test (tests/unit/test_feature.py)
├── Watch fail
├── Implement minimal code (src/news_agent/...)
├── Watch pass
├── Refactor for quality
├── Code review via agent
└── Commit with message
```

### 3. Error Handling Pattern

```python
try:
    result = api_call()
except SpecificError as e:
    log_error()
    retry_with_backoff()
except Exception as e:
    graceful_degradation()
    continue_with_defaults()
```

### 4. Telemetry Pattern

All user-facing operations should:

1. Be decorated with `@traceable(name="operation_name")`
2. Input/output logged automatically
3. LLM calls traced via LiteLLM
4. Metrics visible in LangSmith dashboard

---

## Quick Reference: Adding New Features

### Adding a New Data Source

1. **Create API client** in `src/news_agent/mcp/source_client.py`
   ```python
   def fetch_data(self, no_cache: bool) -> dict:
       # Implement fetching logic
       # Use cache manager
       # Return structured data
   ```

2. **Add to Tool Registry** in `src/news_agent/agent/tools.py`
   ```python
   self.tools["fetch_new_source"] = self.source_client.fetch_data
   ```

3. **Add to Agent** in `src/news_agent/agent/react_agent.py`
   ```python
   @traceable(name="collect_new_source")
   def _collect_new_source(self, no_cache: bool) -> list:
       # Call tool
       # Process data
       return data
   ```

4. **Add to Configuration** in `config.toml`
   ```toml
   [sources.newsource]
   enabled = true
   endpoints = [...]
   ```

### Adding LangSmith Tracing to a Function

1. **Import decorator**
   ```python
   from langsmith import traceable
   ```

2. **Decorate function**
   ```python
   @traceable(name="my_operation")
   def my_operation(self, param1: str) -> str:
       # Function implementation
       return result
   ```

3. **Check trace in LangSmith**
   - Run agent: `news-agent --verbose`
   - Visit: `smith.langchain.com`
   - View trace in project: `news-agent`

---

## Troubleshooting Telemetry

### Traces Not Appearing in LangSmith

**Checklist:**
1. ✅ `LANGSMITH_API_KEY` set in `.env`
2. ✅ API key is valid (check via web UI)
3. ✅ `LANGSMITH_TRACING=true` enabled (set automatically by CLI)
4. ✅ Function decorated with `@traceable`
5. ✅ LLM calls made during execution
6. ✅ Project name matches: `LANGSMITH_PROJECT=news-agent`

**Debug Steps:**
```bash
# Test minimal tracing
python3 test_langsmith_tracing.py

# Check environment
echo $LANGSMITH_API_KEY
echo $LANGSMITH_PROJECT

# Run with verbose logging
news-agent --verbose

# Check LLM logs for "success_handler" confirmation
news-agent --verbose 2>&1 | grep "success_handler"
```

### LLM Traces Show No Token Data

**Cause:** LiteLLM wrapper not properly capturing response

**Solution:**
- Ensure `completion()` call returns proper OpenAI format response
- Check response has `.usage.prompt_tokens` field
- Verify model provides token counts

---

## Understanding the Codebase

### Reading Order for New Developers

1. **Start here:** `src/news_agent/cli.py`
   - Entry point
   - Configuration loading
   - Telemetry enablement

2. **Then:** `src/news_agent/agent/react_agent.py`
   - Main orchestration logic
   - Phase separation
   - Tool invocation pattern

3. **Then:** `src/news_agent/llm/provider.py`
   - LLM integration
   - Multi-provider support
   - Tracing setup

4. **Then:** Data clients
   - `src/news_agent/mcp/github_client.py`
   - `src/news_agent/mcp/hn_client.py`

5. **Finally:** Analysis
   - `src/news_agent/analysis/relevance.py`
   - `src/news_agent/analysis/ranking.py`

### Key Files by Purpose

| Purpose | File | Key Class/Function |
|---------|------|-------------------|
| Entry point | `cli.py` | `run()` command |
| Orchestration | `agent/react_agent.py` | `NewsAgent.run()` |
| LLM integration | `llm/provider.py` | `LLMProvider.complete()` |
| GitHub fetching | `mcp/github_client.py` | `fetch_trending_repos()` |
| HN fetching | `mcp/hn_client.py` | `fetch_posts()` |
| Relevance scoring | `analysis/relevance.py` | `RelevanceScorer.score()` |
| Ranking | `analysis/ranking.py` | `Ranker.rank()` |
| Caching | `cache/manager.py` | `CacheManager` |
| Configuration | `config/models.py` | Pydantic models |
| Output | `output/markdown.py` | `MarkdownGenerator` |
| Telemetry | `cli.py` | LANGSMITH_TRACING env var |

---

## Performance Considerations

### Execution Timeline (Typical Run)

```mermaid
gantt
    title Typical Agent Execution Timeline
    dateFormat YYYY-MM-DD HH:mm:ss

    section Data Collection
    GitHub API         :gh, 2025-11-16 10:19:00, 1s
    HN API            :hn, after gh, 2s

    section Analysis
    Batch 1 (posts 1-5)    :llm1, after hn, 4s
    Batch 2 (posts 6-10)   :llm2, after llm1, 4s
    Batch 3 (posts 11-15)  :llm3, after llm2, 4s
    Batch 4 (posts 16-20)  :llm4, after llm3, 4s
    Batch 5 (posts 21-25)  :llm5, after llm4, 4s
    Batch 6 (posts 26-29)  :llm6, after llm5, 4s

    section Output
    Ranking            :rank, after llm6, 1s
    Report Generation  :report, after rank, 2s

    section Total
    Total Execution    :crit, 2025-11-16 10:19:00, 32s
```

### Optimization Opportunities

1. **Parallel batching**: HN fetches use `asyncio.gather()` - ~10x speedup
2. **Caching**: TTL-based caching reduces redundant API calls
3. **Batch scoring**: Groups posts into batches - reduces LLM calls from 29 to 6
4. **Exponential backoff**: Retries with increasing delays for transient failures

---

## Contributing Guidelines

### Code Review Criteria

- ✅ Tests written first (TDD)
- ✅ All tests passing
- ✅ Code follows project patterns
- ✅ Error handling present
- ✅ Logging added for debuggability
- ✅ Telemetry/tracing considered
- ✅ Documentation updated

### Commit Message Format

```
<type>: <brief description>

<longer explanation if needed>

Related to: <issue number or feature>
```

**Types:** feat, fix, refactor, docs, test, chore

---

## Resources

- **LangSmith Docs**: https://docs.langsmith.com/
- **LiteLLM Docs**: https://docs.litellm.ai/
- **GitHub API**: https://docs.github.com/en/rest
- **HN API**: https://github.com/HackerNews/API
- **Pydantic**: https://pydantic.dev/
- **Click CLI**: https://click.palletsprojects.com/
- **Rich**: https://rich.readthedocs.io/

---

**Last Updated:** November 16, 2025
**Maintained By:** Development Team
