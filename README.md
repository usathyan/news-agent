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
