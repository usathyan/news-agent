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
