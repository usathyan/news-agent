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
