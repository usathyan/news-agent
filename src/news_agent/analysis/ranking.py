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
