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
