# News Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI-based news aggregation agent that collects, analyzes, and reports on GitHub Trending and Hacker News content using Claude Agent SDK with MCP integrations.

**Architecture:** Agent-centric design with ReACT agent orchestrating MCP tool handlers (GitHub, HN). LiteLLM provides multi-provider LLM access for AI-powered relevance scoring, summarization, and ranking. Smart caching with configurable analysis depth.

**Tech Stack:** Python 3.11+, Claude Agent SDK, LiteLLM, MCP (GitHub official + mcp-hn), Rich (terminal UI), TOML (config)

---

## Task 1: Project Foundation Setup

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`
- Create: `config.toml`

**Step 1: Create pyproject.toml with dependencies**

```toml
[project]
name = "news-agent"
version = "0.1.0"
description = "AI-powered news aggregation agent with MCP integrations"
requires-python = ">=3.11"
dependencies = [
    "anthropic-sdk>=0.18.0",
    "litellm>=1.30.0",
    "rich>=13.7.0",
    "tomli>=2.0.1",
    "tomli-w>=1.0.0",
    "httpx>=0.27.0",
    "click>=8.1.7",
    "pydantic>=2.6.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]

[project.scripts]
news-agent = "news_agent.__main__:main"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
```

**Step 2: Create .env.example**

```bash
# LLM Provider API Keys (choose one or more)
OPENROUTER_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_key_here
AZURE_API_KEY=your_key_here

# GitHub MCP Server (if needed)
GITHUB_TOKEN=your_token_here
```

**Step 3: Create .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
.cache/
reports/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
.mypy_cache/
.ruff_cache/
```

**Step 4: Create basic README.md**

```markdown
# News Agent

AI-powered news aggregation agent that collects and analyzes content from GitHub Trending and Hacker News.

## Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Then run
news-agent run
```

## Configuration

Edit `config.toml` to customize sources, analysis depth, and output settings.
```

**Step 5: Create config.toml**

```toml
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
depth = "medium"
top_n = 25

[sources.github]
enabled = true
mcp_server = "remote"
categories = ["repositories", "developers"]

[sources.hackernews]
enabled = true
mcp_server = "local"
endpoints = ["newest", "show"]
filter_topics = ["AI", "ML", "GenAI", "LLM", "machine learning"]

[ranking]
strategy = "balanced"

[ranking.weights]
relevance = 0.7
popularity = 0.3

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

**Step 6: Create project directory structure**

Run:
```bash
mkdir -p src/news_agent/{agent,mcp,llm,analysis,cache,output,config,utils}
mkdir -p tests/{unit,integration}
mkdir -p .cache reports
touch src/news_agent/__init__.py
touch src/news_agent/{agent,mcp,llm,analysis,cache,output,config,utils}/__init__.py
```

**Step 7: Install project in development mode**

Run: `pip install -e ".[dev]"`
Expected: Successfully installed news-agent

**Step 8: Commit foundation**

```bash
git init
git add .
git commit -m "feat: initial project structure and configuration"
```

---

## Task 2: Configuration Loader

**Files:**
- Create: `src/news_agent/config/models.py`
- Create: `src/news_agent/config/loader.py`
- Create: `tests/unit/test_config_loader.py`

**Step 1: Write failing test for config loader**

Create `tests/unit/test_config_loader.py`:

```python
import tempfile
from pathlib import Path
import pytest
from news_agent.config.loader import load_config
from news_agent.config.models import Config


def test_load_config_from_toml():
    """Test loading configuration from TOML file"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
depth = "medium"
top_n = 25
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        config = load_config(config_path)
        assert config.llm.provider == "anthropic"
        assert config.analysis.depth == "medium"
        assert config.analysis.top_n == 25
    finally:
        config_path.unlink()


def test_config_validation_fails_on_invalid_depth():
    """Test config validation catches invalid depth values"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
depth = "invalid"
top_n = 25
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValueError):
            load_config(config_path)
    finally:
        config_path.unlink()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_config_loader.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'news_agent.config.loader'"

**Step 3: Create config models**

Create `src/news_agent/config/models.py`:

```python
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key_env: str


class AnalysisConfig(BaseModel):
    depth: Literal["lightweight", "medium", "deep"] = "medium"
    top_n: int = Field(default=25, ge=1, le=100)


class SourceConfig(BaseModel):
    enabled: bool = True


class GitHubSourceConfig(SourceConfig):
    mcp_server: str = "remote"
    categories: list[str] = Field(default_factory=lambda: ["repositories"])


class HackerNewsSourceConfig(SourceConfig):
    mcp_server: str = "local"
    endpoints: list[str] = Field(default_factory=lambda: ["newest"])
    filter_topics: list[str] = Field(default_factory=list)


class SourcesConfig(BaseModel):
    github: GitHubSourceConfig = Field(default_factory=GitHubSourceConfig)
    hackernews: HackerNewsSourceConfig = Field(default_factory=HackerNewsSourceConfig)


class RankingWeights(BaseModel):
    relevance: float = Field(default=0.7, ge=0.0, le=1.0)
    popularity: float = Field(default=0.3, ge=0.0, le=1.0)

    @field_validator('popularity')
    @classmethod
    def check_weights_sum(cls, v: float, info) -> float:
        relevance = info.data.get('relevance', 0.7)
        if abs(relevance + v - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        return v


class RankingConfig(BaseModel):
    strategy: Literal["popularity", "relevance", "balanced"] = "balanced"
    weights: RankingWeights = Field(default_factory=RankingWeights)


class CachingConfig(BaseModel):
    enabled: bool = True
    ttl_hours: int = Field(default=1, ge=0)


class OutputConfig(BaseModel):
    format: Literal["markdown"] = "markdown"
    save_path: str = "./reports"
    terminal_preview: bool = True


class RetryConfig(BaseModel):
    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_multiplier: int = Field(default=2, ge=1)
    graceful_degradation: bool = True


class Config(BaseModel):
    llm: LLMConfig
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    sources: SourcesConfig = Field(default_factory=SourcesConfig)
    ranking: RankingConfig = Field(default_factory=RankingConfig)
    caching: CachingConfig = Field(default_factory=CachingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
```

**Step 4: Create config loader**

Create `src/news_agent/config/loader.py`:

```python
from pathlib import Path
import tomli
from news_agent.config.models import Config


def load_config(config_path: Path) -> Config:
    """Load and validate configuration from TOML file"""
    with open(config_path, 'rb') as f:
        config_dict = tomli.load(f)

    return Config(**config_dict)
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_config_loader.py -v`
Expected: PASS (2 tests)

**Step 6: Commit config loader**

```bash
git add src/news_agent/config/ tests/unit/test_config_loader.py
git commit -m "feat: add TOML configuration loader with validation"
```

---

## Task 3: LiteLLM Provider Integration

**Files:**
- Create: `src/news_agent/llm/provider.py`
- Create: `tests/unit/test_llm_provider.py`

**Step 1: Write failing test for LLM provider**

Create `tests/unit/test_llm_provider.py`:

```python
import os
import pytest
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import LLMConfig


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="ANTHROPIC_API_KEY"
    )


def test_llm_provider_initialization(llm_config):
    """Test LLM provider initializes correctly"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    provider = LLMProvider(llm_config)
    assert provider.model == "claude-3-5-sonnet-20241022"


def test_llm_provider_missing_api_key():
    """Test provider raises error when API key missing"""
    config = LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="MISSING_KEY"
    )
    if "MISSING_KEY" in os.environ:
        del os.environ["MISSING_KEY"]

    with pytest.raises(ValueError, match="API key not found"):
        LLMProvider(config)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_llm_provider.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'news_agent.llm.provider'"

**Step 3: Create LLM provider**

Create `src/news_agent/llm/provider.py`:

```python
import os
from typing import Any
from litellm import completion
from news_agent.config.models import LLMConfig


class LLMProvider:
    """Wrapper for LiteLLM to support multiple LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model

        # Verify API key exists
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable: {config.api_key_env}"
            )

        # Set API key for litellm
        os.environ[f"{config.provider.upper()}_API_KEY"] = api_key

    def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any
    ) -> str:
        """Generate completion using configured LLM provider"""
        response = completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    def complete_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any
    ) -> str:
        """Generate JSON completion"""
        return self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_llm_provider.py -v`
Expected: PASS (2 tests)

**Step 5: Commit LLM provider**

```bash
git add src/news_agent/llm/ tests/unit/test_llm_provider.py
git commit -m "feat: add LiteLLM provider wrapper for multi-provider support"
```

---

## Task 4: Cache Manager

**Files:**
- Create: `src/news_agent/cache/manager.py`
- Create: `tests/unit/test_cache_manager.py`

**Step 1: Write failing test for cache manager**

Create `tests/unit/test_cache_manager.py`:

```python
import tempfile
from pathlib import Path
import json
import time
import pytest
from news_agent.cache.manager import CacheManager
from news_agent.config.models import CachingConfig


@pytest.fixture
def cache_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cache_config():
    return CachingConfig(enabled=True, ttl_hours=1)


def test_cache_set_and_get(cache_dir, cache_config):
    """Test setting and getting cached data"""
    cache = CacheManager(cache_dir, cache_config)

    test_data = {"key": "value", "items": [1, 2, 3]}
    cache.set("test_key", test_data)

    retrieved = cache.get("test_key")
    assert retrieved == test_data


def test_cache_expiration(cache_dir):
    """Test cache expires after TTL"""
    # Set very short TTL for testing
    config = CachingConfig(enabled=True, ttl_hours=0.0001)  # ~0.36 seconds
    cache = CacheManager(cache_dir, config)

    cache.set("test_key", {"data": "value"})
    assert cache.get("test_key") is not None

    time.sleep(0.5)
    assert cache.get("test_key") is None


def test_cache_disabled(cache_dir):
    """Test cache returns None when disabled"""
    config = CachingConfig(enabled=False, ttl_hours=1)
    cache = CacheManager(cache_dir, config)

    cache.set("test_key", {"data": "value"})
    assert cache.get("test_key") is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_cache_manager.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create cache manager**

Create `src/news_agent/cache/manager.py`:

```python
import json
import time
from pathlib import Path
from typing import Any, Optional
from news_agent.config.models import CachingConfig


class CacheManager:
    """Manages file-based caching with TTL support"""

    def __init__(self, cache_dir: Path, config: CachingConfig):
        self.cache_dir = cache_dir
        self.config = config
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for given key"""
        # Use hash to avoid filesystem issues with special chars
        safe_key = key.replace('/', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.json"

    def set(self, key: str, data: Any) -> None:
        """Store data in cache with current timestamp"""
        if not self.config.enabled:
            return

        cache_path = self._get_cache_path(key)
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }

        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache if not expired"""
        if not self.config.enabled:
            return None

        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        # Check if expired
        age_hours = (time.time() - cache_data["timestamp"]) / 3600
        if age_hours > self.config.ttl_hours:
            cache_path.unlink()
            return None

        return cache_data["data"]

    def clear(self, key: Optional[str] = None) -> None:
        """Clear specific cache entry or all cache"""
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_cache_manager.py -v`
Expected: PASS (3 tests)

**Step 5: Commit cache manager**

```bash
git add src/news_agent/cache/ tests/unit/test_cache_manager.py
git commit -m "feat: add cache manager with TTL support"
```

---

## Task 5: Retry Logic Utility

**Files:**
- Create: `src/news_agent/utils/retry.py`
- Create: `tests/unit/test_retry.py`

**Step 1: Write failing test for retry logic**

Create `tests/unit/test_retry.py`:

```python
import pytest
from news_agent.utils.retry import retry_with_backoff
from news_agent.config.models import RetryConfig


def test_retry_succeeds_on_first_attempt():
    """Test successful execution on first try"""
    config = RetryConfig(max_attempts=3, backoff_multiplier=2)

    call_count = 0

    def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = retry_with_backoff(successful_func, config)
    assert result == "success"
    assert call_count == 1


def test_retry_succeeds_after_failures():
    """Test retry succeeds after initial failures"""
    config = RetryConfig(max_attempts=3, backoff_multiplier=1)

    call_count = 0

    def eventually_succeeds():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Network error")
        return "success"

    result = retry_with_backoff(eventually_succeeds, config)
    assert result == "success"
    assert call_count == 3


def test_retry_fails_after_max_attempts():
    """Test retry gives up after max attempts"""
    config = RetryConfig(max_attempts=3, backoff_multiplier=1, graceful_degradation=False)

    def always_fails():
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        retry_with_backoff(always_fails, config)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_retry.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create retry utility**

Create `src/news_agent/utils/retry.py`:

```python
import time
from typing import TypeVar, Callable
from news_agent.config.models import RetryConfig

T = TypeVar('T')


def retry_with_backoff(
    func: Callable[[], T],
    config: RetryConfig,
    retryable_exceptions: tuple = (ConnectionError, TimeoutError)
) -> T:
    """Execute function with exponential backoff retry logic"""
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return func()
        except retryable_exceptions as e:
            last_exception = e

            if attempt < config.max_attempts - 1:
                # Calculate backoff delay
                delay = config.backoff_multiplier ** attempt
                time.sleep(delay)
            else:
                # Last attempt failed
                if config.graceful_degradation:
                    return None  # type: ignore
                else:
                    raise

    # This shouldn't be reached, but for type safety
    if not config.graceful_degradation and last_exception:
        raise last_exception
    return None  # type: ignore
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_retry.py -v`
Expected: PASS (3 tests)

**Step 5: Commit retry utility**

```bash
git add src/news_agent/utils/ tests/unit/test_retry.py
git commit -m "feat: add retry logic with exponential backoff"
```

---

## Task 6: GitHub MCP Client

**Files:**
- Create: `src/news_agent/mcp/github_client.py`
- Create: `tests/integration/test_github_mcp.py`

**Step 1: Write integration test for GitHub MCP**

Create `tests/integration/test_github_mcp.py`:

```python
import pytest
from news_agent.mcp.github_client import GitHubMCPClient
from news_agent.config.models import GitHubSourceConfig


@pytest.fixture
def github_config():
    return GitHubSourceConfig(
        enabled=True,
        mcp_server="remote",
        categories=["repositories"]
    )


@pytest.mark.skip(reason="Requires GitHub MCP server running")
def test_fetch_trending_repositories(github_config):
    """Test fetching trending repositories via MCP"""
    client = GitHubMCPClient(github_config)

    repos = client.fetch_trending_repositories()

    assert len(repos) > 0
    assert "name" in repos[0]
    assert "url" in repos[0]
    assert "stars" in repos[0]
    assert "description" in repos[0]
```

**Step 2: Create GitHub MCP client stub**

Create `src/news_agent/mcp/github_client.py`:

```python
from typing import Any
from news_agent.config.models import GitHubSourceConfig


class GitHubMCPClient:
    """Client for interacting with GitHub MCP server"""

    def __init__(self, config: GitHubSourceConfig):
        self.config = config
        # TODO: Initialize MCP connection in Phase 2
        # For now, this is a stub for the architecture

    def fetch_trending_repositories(self, time_range: str = "daily") -> list[dict[str, Any]]:
        """Fetch trending repositories from GitHub

        Args:
            time_range: One of "daily", "weekly", "monthly"

        Returns:
            List of repository dictionaries with keys:
            - name: Repository name (owner/repo)
            - url: Repository URL
            - description: Repository description
            - stars: Star count
            - forks: Fork count
            - language: Primary language
            - stars_today: Stars gained today
        """
        # TODO: Implement MCP call
        # This will use Claude Agent SDK's MCP integration
        # For now, return empty list
        return []

    def fetch_trending_developers(self, time_range: str = "daily") -> list[dict[str, Any]]:
        """Fetch trending developers from GitHub

        Returns:
            List of developer dictionaries
        """
        # TODO: Implement MCP call
        return []
```

**Step 3: Commit GitHub MCP client stub**

```bash
git add src/news_agent/mcp/github_client.py tests/integration/test_github_mcp.py
git commit -m "feat: add GitHub MCP client stub (implementation pending)"
```

---

## Task 7: Hacker News MCP Client

**Files:**
- Create: `src/news_agent/mcp/hn_client.py`
- Create: `tests/integration/test_hn_mcp.py`

**Step 1: Write integration test for HN MCP**

Create `tests/integration/test_hn_mcp.py`:

```python
import pytest
from news_agent.mcp.hn_client import HackerNewsMCPClient
from news_agent.config.models import HackerNewsSourceConfig


@pytest.fixture
def hn_config():
    return HackerNewsSourceConfig(
        enabled=True,
        mcp_server="local",
        endpoints=["newest"],
        filter_topics=["AI", "ML"]
    )


@pytest.mark.skip(reason="Requires HN MCP server running")
def test_fetch_newest_posts(hn_config):
    """Test fetching newest posts via MCP"""
    client = HackerNewsMCPClient(hn_config)

    posts = client.fetch_posts("newest", limit=10)

    assert len(posts) > 0
    assert "title" in posts[0]
    assert "url" in posts[0]
    assert "score" in posts[0]
```

**Step 2: Create HN MCP client stub**

Create `src/news_agent/mcp/hn_client.py`:

```python
from typing import Any, Literal
from news_agent.config.models import HackerNewsSourceConfig


class HackerNewsMCPClient:
    """Client for interacting with Hacker News MCP server"""

    def __init__(self, config: HackerNewsSourceConfig):
        self.config = config
        # TODO: Initialize MCP connection

    def fetch_posts(
        self,
        endpoint: Literal["newest", "show", "ask", "job"],
        limit: int = 30
    ) -> list[dict[str, Any]]:
        """Fetch posts from Hacker News

        Args:
            endpoint: HN endpoint to query
            limit: Maximum number of posts to fetch

        Returns:
            List of post dictionaries with keys:
            - id: Post ID
            - title: Post title
            - url: Post URL (may be None for Ask HN)
            - score: Points/votes
            - by: Author username
            - time: Unix timestamp
            - descendants: Comment count
        """
        # TODO: Implement MCP call
        return []

    def fetch_comments(self, post_id: int) -> list[dict[str, Any]]:
        """Fetch comments for a post

        Returns:
            List of comment dictionaries
        """
        # TODO: Implement MCP call
        return []
```

**Step 3: Commit HN MCP client stub**

```bash
git add src/news_agent/mcp/hn_client.py tests/integration/test_hn_mcp.py
git commit -m "feat: add Hacker News MCP client stub (implementation pending)"
```

---

## Task 8: Relevance Scoring

**Files:**
- Create: `src/news_agent/analysis/relevance.py`
- Create: `tests/unit/test_relevance.py`

**Step 1: Write failing test for relevance scoring**

Create `tests/unit/test_relevance.py`:

```python
import pytest
from news_agent.analysis.relevance import RelevanceScorer
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import LLMConfig, AnalysisConfig


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="ANTHROPIC_API_KEY"
    )


@pytest.fixture
def analysis_config():
    return AnalysisConfig(depth="medium", top_n=25)


@pytest.mark.skip(reason="Requires API key")
def test_score_hn_post_relevance(llm_config, analysis_config):
    """Test scoring HN post relevance to AI/ML topics"""
    provider = LLMProvider(llm_config)
    scorer = RelevanceScorer(provider, analysis_config)

    post = {
        "title": "New GPT-4 model released with vision capabilities",
        "url": "https://example.com/gpt4-vision",
        "text": "OpenAI announces GPT-4 with image understanding..."
    }

    score = scorer.score_hn_post(post, topics=["AI", "ML", "GenAI"])

    assert 0.0 <= score <= 1.0
    assert score > 0.7  # Should be highly relevant
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_relevance.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create relevance scorer**

Create `src/news_agent/analysis/relevance.py`:

```python
import json
from typing import Any
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import AnalysisConfig


class RelevanceScorer:
    """Score content relevance using LLM"""

    def __init__(self, llm_provider: LLMProvider, config: AnalysisConfig):
        self.llm = llm_provider
        self.config = config

    def score_hn_post(self, post: dict[str, Any], topics: list[str]) -> float:
        """Score a Hacker News post's relevance to specified topics

        Args:
            post: Post dictionary with title, url, text
            topics: List of topics to check relevance against

        Returns:
            Relevance score between 0.0 and 1.0
        """
        prompt = self._build_relevance_prompt(post, topics)

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.llm.complete_json(messages, temperature=0.3)
        result = json.loads(response)

        return float(result.get("relevance_score", 0.0))

    def _build_relevance_prompt(self, post: dict[str, Any], topics: list[str]) -> str:
        """Build prompt for relevance scoring"""
        topics_str = ", ".join(topics)

        return f"""Score the relevance of this Hacker News post to topics: {topics_str}

Post Title: {post.get('title', 'N/A')}
Post URL: {post.get('url', 'N/A')}
Post Text: {post.get('text', 'N/A')[:500]}

Analyze how relevant this post is to {topics_str}. Consider:
- Direct mentions or discussions of these topics
- Related concepts, tools, or techniques
- Practical applications or research
- Community interest and significance

Return a JSON object with:
{{
  "relevance_score": <float between 0.0 and 1.0>,
  "reasoning": "<brief explanation>",
  "key_topics": ["<topic1>", "<topic2>"]
}}

Score 1.0 = Highly relevant (directly about topic)
Score 0.5 = Moderately relevant (tangentially related)
Score 0.0 = Not relevant (unrelated)"""
```

**Step 4: Run test (will skip due to API requirement)**

Run: `pytest tests/unit/test_relevance.py -v`
Expected: SKIP (requires API key)

**Step 5: Commit relevance scorer**

```bash
git add src/news_agent/analysis/relevance.py tests/unit/test_relevance.py
git commit -m "feat: add AI-powered relevance scoring for HN posts"
```

---

## Task 9: Summarization

**Files:**
- Create: `src/news_agent/analysis/summarization.py`
- Create: `tests/unit/test_summarization.py`

**Step 1: Write test for summarization**

Create `tests/unit/test_summarization.py`:

```python
import pytest
from news_agent.analysis.summarization import Summarizer
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import LLMConfig, AnalysisConfig


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="ANTHROPIC_API_KEY"
    )


@pytest.mark.skip(reason="Requires API key")
def test_summarize_article(llm_config):
    """Test article summarization at different depths"""
    provider = LLMProvider(llm_config)

    # Test lightweight
    config = AnalysisConfig(depth="lightweight", top_n=25)
    summarizer = Summarizer(provider, config)

    article = {
        "title": "New AI Model Breakthrough",
        "url": "https://example.com/article",
        "text": "Researchers announce a new AI model that achieves state-of-the-art results..."
    }

    summary = summarizer.summarize_article(article)
    assert len(summary) > 0
    assert len(summary) < 200  # Lightweight should be brief
```

**Step 2: Create summarizer**

Create `src/news_agent/analysis/summarization.py`:

```python
from typing import Any
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import AnalysisConfig


class Summarizer:
    """Generate summaries of articles and comments"""

    def __init__(self, llm_provider: LLMProvider, config: AnalysisConfig):
        self.llm = llm_provider
        self.config = config

    def summarize_article(self, article: dict[str, Any]) -> str:
        """Summarize an article based on configured depth

        Args:
            article: Article dictionary with title, url, text

        Returns:
            Summary string
        """
        prompt = self._build_article_summary_prompt(article)

        messages = [
            {"role": "user", "content": prompt}
        ]

        max_tokens = self._get_max_tokens_for_depth()
        return self.llm.complete(messages, temperature=0.5, max_tokens=max_tokens)

    def summarize_comments(self, comments: list[dict[str, Any]]) -> str:
        """Summarize key themes from comments

        Args:
            comments: List of comment dictionaries

        Returns:
            Summary of comment themes
        """
        if not comments:
            return "No comments available"

        prompt = self._build_comments_summary_prompt(comments)

        messages = [
            {"role": "user", "content": prompt}
        ]

        max_tokens = self._get_max_tokens_for_depth()
        return self.llm.complete(messages, temperature=0.5, max_tokens=max_tokens)

    def _build_article_summary_prompt(self, article: dict[str, Any]) -> str:
        """Build prompt for article summarization"""
        depth_instructions = {
            "lightweight": "Provide a one-sentence summary (max 50 words).",
            "medium": "Provide a concise summary (2-3 sentences, max 100 words) covering key points.",
            "deep": "Provide a comprehensive summary (4-5 sentences, max 200 words) including context, implications, and significance."
        }

        instruction = depth_instructions.get(self.config.depth, depth_instructions["medium"])

        return f"""Summarize this article:

Title: {article.get('title', 'N/A')}
URL: {article.get('url', 'N/A')}
Content: {article.get('text', 'N/A')[:2000]}

{instruction}"""

    def _build_comments_summary_prompt(self, comments: list[dict[str, Any]]) -> str:
        """Build prompt for comment summarization"""
        comments_text = "\n\n".join([
            f"Comment by {c.get('by', 'unknown')}: {c.get('text', '')[:300]}"
            for c in comments[:10]  # Limit to top 10 comments
        ])

        depth_instructions = {
            "lightweight": "List 2-3 key discussion themes (one sentence).",
            "medium": "Summarize main discussion themes and notable perspectives (2-3 sentences).",
            "deep": "Provide detailed analysis of discussion themes, sentiment, consensus/disagreement, and notable insights (4-5 sentences)."
        }

        instruction = depth_instructions.get(self.config.depth, depth_instructions["medium"])

        return f"""Analyze these comments and {instruction}

{comments_text}"""

    def _get_max_tokens_for_depth(self) -> int:
        """Get max tokens based on analysis depth"""
        return {
            "lightweight": 128,
            "medium": 256,
            "deep": 512
        }.get(self.config.depth, 256)
```

**Step 3: Commit summarizer**

```bash
git add src/news_agent/analysis/summarization.py tests/unit/test_summarization.py
git commit -m "feat: add depth-configurable summarization for articles and comments"
```

---

## Task 10: Ranking Strategy

**Files:**
- Create: `src/news_agent/analysis/ranking.py`
- Create: `tests/unit/test_ranking.py`

**Step 1: Write failing test for ranking**

Create `tests/unit/test_ranking.py`:

```python
import pytest
from news_agent.analysis.ranking import Ranker
from news_agent.config.models import RankingConfig, RankingWeights


def test_balanced_ranking():
    """Test balanced ranking strategy"""
    config = RankingConfig(
        strategy="balanced",
        weights=RankingWeights(relevance=0.7, popularity=0.3)
    )
    ranker = Ranker(config)

    items = [
        {"id": 1, "relevance_score": 0.9, "popularity_score": 0.3},
        {"id": 2, "relevance_score": 0.5, "popularity_score": 0.9},
        {"id": 3, "relevance_score": 0.8, "popularity_score": 0.8},
    ]

    ranked = ranker.rank(items)

    # Item 3 should be first (high relevance and popularity)
    assert ranked[0]["id"] == 3
    # Item 1 should be second (higher relevance weight)
    assert ranked[1]["id"] == 1


def test_popularity_ranking():
    """Test popularity-only ranking"""
    config = RankingConfig(strategy="popularity")
    ranker = Ranker(config)

    items = [
        {"id": 1, "popularity_score": 0.3},
        {"id": 2, "popularity_score": 0.9},
        {"id": 3, "popularity_score": 0.6},
    ]

    ranked = ranker.rank(items)
    assert ranked[0]["id"] == 2
    assert ranked[1]["id"] == 3
    assert ranked[2]["id"] == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_ranking.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create ranker**

Create `src/news_agent/analysis/ranking.py`:

```python
from typing import Any
from news_agent.config.models import RankingConfig


class Ranker:
    """Rank items based on configured strategy"""

    def __init__(self, config: RankingConfig):
        self.config = config

    def rank(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Rank items based on configured strategy

        Args:
            items: List of items with relevance_score and/or popularity_score

        Returns:
            Sorted list of items (highest ranked first)
        """
        if self.config.strategy == "popularity":
            return self._rank_by_popularity(items)
        elif self.config.strategy == "relevance":
            return self._rank_by_relevance(items)
        else:  # balanced
            return self._rank_balanced(items)

    def _rank_by_popularity(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Rank by popularity score only"""
        return sorted(items, key=lambda x: x.get("popularity_score", 0), reverse=True)

    def _rank_by_relevance(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Rank by relevance score only"""
        return sorted(items, key=lambda x: x.get("relevance_score", 0), reverse=True)

    def _rank_balanced(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Rank by weighted combination of relevance and popularity"""
        def calculate_score(item: dict[str, Any]) -> float:
            relevance = item.get("relevance_score", 0)
            popularity = item.get("popularity_score", 0)

            return (
                relevance * self.config.weights.relevance +
                popularity * self.config.weights.popularity
            )

        return sorted(items, key=calculate_score, reverse=True)

    def normalize_scores(self, items: list[dict[str, Any]], score_field: str) -> list[dict[str, Any]]:
        """Normalize scores to 0-1 range

        Args:
            items: List of items
            score_field: Field name containing score to normalize

        Returns:
            Items with normalized scores
        """
        if not items:
            return items

        scores = [item.get(score_field, 0) for item in items]
        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            # All scores are the same
            for item in items:
                item[f"{score_field}_normalized"] = 0.5
            return items

        for item in items:
            original = item.get(score_field, 0)
            normalized = (original - min_score) / (max_score - min_score)
            item[f"{score_field}_normalized"] = normalized

        return items
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_ranking.py -v`
Expected: PASS (2 tests)

**Step 5: Commit ranker**

```bash
git add src/news_agent/analysis/ranking.py tests/unit/test_ranking.py
git commit -m "feat: add configurable ranking strategy with weighted scoring"
```

---

## Task 11: Markdown Report Generator

**Files:**
- Create: `src/news_agent/output/markdown.py`
- Create: `tests/unit/test_markdown_output.py`

**Step 1: Write failing test for markdown generation**

Create `tests/unit/test_markdown_output.py`:

```python
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
    assert "1234" in markdown  # stars
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_markdown_output.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create markdown generator**

Create `src/news_agent/output/markdown.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_markdown_output.py -v`
Expected: PASS (2 tests)

**Step 5: Commit markdown generator**

```bash
git add src/news_agent/output/markdown.py tests/unit/test_markdown_output.py
git commit -m "feat: add markdown report generator"
```

---

## Task 12: Terminal Output with Rich

**Files:**
- Create: `src/news_agent/output/terminal.py`
- Create: `tests/unit/test_terminal_output.py`

**Step 1: Write test for terminal output**

Create `tests/unit/test_terminal_output.py`:

```python
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
```

**Step 2: Create terminal display**

Create `src/news_agent/output/terminal.py`:

```python
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
```

**Step 3: Commit terminal display**

```bash
git add src/news_agent/output/terminal.py tests/unit/test_terminal_output.py
git commit -m "feat: add rich terminal output with tables and progress"
```

---

## Task 13: CLI Entry Point

**Files:**
- Create: `src/news_agent/__main__.py`
- Create: `src/news_agent/cli.py`

**Step 1: Create CLI module with click**

Create `src/news_agent/cli.py`:

```python
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
```

**Step 2: Create __main__.py**

Create `src/news_agent/__main__.py`:

```python
from news_agent.cli import main

if __name__ == "__main__":
    main()
```

**Step 3: Test CLI**

Run: `news-agent --help`
Expected: Shows help message with all options

Run: `news-agent --dry-run`
Expected: Shows dry run message

**Step 4: Commit CLI**

```bash
git add src/news_agent/__main__.py src/news_agent/cli.py
git commit -m "feat: add CLI entry point with click"
```

---

## Task 14: Agent Integration (Claude Agent SDK)

**Files:**
- Create: `src/news_agent/agent/react_agent.py`
- Create: `src/news_agent/agent/tools.py`
- Create: `tests/integration/test_agent.py`

**Note:** This task requires Claude Agent SDK implementation. Since the SDK is still evolving, this provides the architectural skeleton. Full implementation will depend on the SDK's MCP integration patterns.

**Step 1: Create tool definitions**

Create `src/news_agent/agent/tools.py`:

```python
from typing import Any, Callable
from news_agent.mcp.github_client import GitHubMCPClient
from news_agent.mcp.hn_client import HackerNewsMCPClient
from news_agent.analysis.relevance import RelevanceScorer
from news_agent.analysis.ranking import Ranker
from news_agent.cache.manager import CacheManager


class ToolRegistry:
    """Registry of tools available to the agent"""

    def __init__(
        self,
        github_client: GitHubMCPClient,
        hn_client: HackerNewsMCPClient,
        relevance_scorer: RelevanceScorer,
        ranker: Ranker,
        cache_manager: CacheManager
    ):
        self.github_client = github_client
        self.hn_client = hn_client
        self.relevance_scorer = relevance_scorer
        self.ranker = ranker
        self.cache = cache_manager

        self.tools = self._register_tools()

    def _register_tools(self) -> dict[str, Callable]:
        """Register all available tools"""
        return {
            "fetch_github_trending": self._fetch_github_trending,
            "fetch_hn_posts": self._fetch_hn_posts,
            "score_relevance": self._score_relevance,
            "rank_items": self._rank_items,
        }

    def _fetch_github_trending(self, **kwargs: Any) -> dict[str, Any]:
        """Tool: Fetch GitHub trending repositories"""
        cache_key = "github_trending"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached and not kwargs.get("no_cache"):
            return {"source": "cache", "data": cached}

        # Fetch fresh data
        repos = self.github_client.fetch_trending_repositories()

        # Cache results
        self.cache.set(cache_key, repos)

        return {"source": "mcp", "data": repos}

    def _fetch_hn_posts(self, endpoint: str = "newest", **kwargs: Any) -> dict[str, Any]:
        """Tool: Fetch Hacker News posts"""
        cache_key = f"hn_{endpoint}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached and not kwargs.get("no_cache"):
            return {"source": "cache", "data": cached}

        # Fetch fresh data
        posts = self.hn_client.fetch_posts(endpoint)

        # Cache results
        self.cache.set(cache_key, posts)

        return {"source": "mcp", "data": posts}

    def _score_relevance(self, items: list[dict[str, Any]], topics: list[str], **kwargs: Any) -> list[dict[str, Any]]:
        """Tool: Score relevance of items"""
        for item in items:
            score = self.relevance_scorer.score_hn_post(item, topics)
            item["relevance_score"] = score

        return items

    def _rank_items(self, items: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Tool: Rank items based on configured strategy"""
        return self.ranker.rank(items)
```

**Step 2: Create ReACT agent skeleton**

Create `src/news_agent/agent/react_agent.py`:

```python
from typing import Any
from news_agent.config.models import Config
from news_agent.agent.tools import ToolRegistry
from news_agent.llm.provider import LLMProvider


class NewsAgent:
    """ReACT agent using Claude Agent SDK"""

    def __init__(
        self,
        config: Config,
        tool_registry: ToolRegistry,
        llm_provider: LLMProvider
    ):
        self.config = config
        self.tools = tool_registry
        self.llm = llm_provider

        # TODO: Initialize Claude Agent SDK client
        # This will use the SDK's MCP integration

    def run(self, no_cache: bool = False) -> dict[str, Any]:
        """Execute the news aggregation workflow

        Returns:
            Dictionary with collected and analyzed data
        """
        results = {
            "github_repos": [],
            "hn_posts": [],
            "metadata": {
                "sources": [],
                "analysis_depth": self.config.analysis.depth
            }
        }

        # GitHub collection
        if self.config.sources.github.enabled:
            github_data = self._collect_github_data(no_cache)
            results["github_repos"] = github_data
            results["metadata"]["sources"].append("github")

        # Hacker News collection
        if self.config.sources.hackernews.enabled:
            hn_data = self._collect_hn_data(no_cache)
            results["hn_posts"] = hn_data
            results["metadata"]["sources"].append("hackernews")

        return results

    def _collect_github_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """Collect and analyze GitHub trending data"""
        # Fetch trending repos
        result = self.tools.tools["fetch_github_trending"](no_cache=no_cache)
        repos = result["data"]

        # Normalize popularity scores (stars)
        if repos:
            # TODO: Add analysis via LLM for project popularity
            pass

        # Take top N
        return repos[:self.config.analysis.top_n]

    def _collect_hn_data(self, no_cache: bool) -> list[dict[str, Any]]:
        """Collect and analyze Hacker News data"""
        all_posts = []

        # Fetch from configured endpoints
        for endpoint in self.config.sources.hackernews.endpoints:
            result = self.tools.tools["fetch_hn_posts"](endpoint=endpoint, no_cache=no_cache)
            all_posts.extend(result["data"])

        # Score relevance
        topics = self.config.sources.hackernews.filter_topics
        scored_posts = self.tools.tools["score_relevance"](all_posts, topics)

        # Filter by relevance threshold
        relevant_posts = [p for p in scored_posts if p.get("relevance_score", 0) > 0.5]

        # Rank posts
        ranked_posts = self.tools.tools["rank_items"](relevant_posts)

        # Take top N
        return ranked_posts[:self.config.analysis.top_n]
```

**Step 3: Commit agent skeleton**

```bash
git add src/news_agent/agent/
git commit -m "feat: add ReACT agent skeleton with tool registry"
```

---

## Task 15: Wire Up CLI to Agent

**Files:**
- Modify: `src/news_agent/cli.py`

**Step 1: Update CLI to orchestrate agent**

Update `src/news_agent/cli.py`, replace the TODO section with:

```python
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

    # Load environment variables
    load_dotenv()

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
```

**Step 2: Test CLI (will fail at MCP connection)**

Run: `news-agent --dry-run`
Expected: Shows dry run output

**Step 3: Commit CLI integration**

```bash
git add src/news_agent/cli.py
git commit -m "feat: wire up CLI to agent orchestration"
```

---

## Next Steps: MCP Implementation

**Phase 2 Complete - Core Architecture Ready**

The remaining work is to implement the actual MCP connections:

1. **GitHub MCP Integration** - Connect to GitHub's official MCP server
2. **Hacker News MCP Integration** - Set up mcp-hn or build custom MCP
3. **Agent SDK Integration** - Integrate Claude Agent SDK's MCP support

These require:
- MCP server configuration
- Network connectivity to MCP endpoints
- Potential modifications to mcp-hn for our needs

**Testing Strategy:**

1. Unit tests (completed for most components)
2. Integration tests with MCP servers (pending)
3. End-to-end test with real data sources

**Documentation Needed:**

1. Setup guide for MCP servers
2. Configuration examples
3. Troubleshooting guide

---

## Implementation Complete Checklist

- ✅ Project structure and configuration
- ✅ Configuration loader with validation
- ✅ LiteLLM provider integration
- ✅ Cache manager with TTL
- ✅ Retry logic utility
- ✅ GitHub MCP client (stub)
- ✅ HN MCP client (stub)
- ✅ Relevance scoring
- ✅ Summarization
- ✅ Ranking strategy
- ✅ Markdown report generator
- ✅ Rich terminal output
- ✅ CLI with all flags
- ✅ Agent orchestration
- ⏳ MCP server connections (requires external setup)
- ⏳ End-to-end testing with real data
- ⏳ Social media analysis (post-MVP)
- ⏳ Scheduling (post-MVP)
- ⏳ Email delivery (post-MVP)
