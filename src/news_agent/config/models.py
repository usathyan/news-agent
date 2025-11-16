from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator


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

    @model_validator(mode='after')
    def check_weights_sum(self) -> 'RankingWeights':
        if abs(self.relevance + self.popularity - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        return self


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


class TelemetryConfig(BaseModel):
    enabled: bool = True
    backend: Literal["langsmith", "otel", "langfuse"] = "langsmith"
    project_name: str = "news-agent"


class Config(BaseModel):
    llm: LLMConfig
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    sources: SourcesConfig = Field(default_factory=SourcesConfig)
    ranking: RankingConfig = Field(default_factory=RankingConfig)
    caching: CachingConfig = Field(default_factory=CachingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
