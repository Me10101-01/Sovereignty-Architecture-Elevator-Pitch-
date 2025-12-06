"""
Configuration module for SovereignPRManager
Author: SovereignPRManager Legion
"""

import os
from dataclasses import dataclass, field
from typing import Optional


# Named constants for default values
DEFAULT_CONFIDENCE_THRESHOLD = 0.9
DEFAULT_POLL_INTERVAL_SECONDS = 10
DEFAULT_MAX_DIFF_SIZE = 10000
DEFAULT_NATS_URL = "nats://localhost:4222"


@dataclass
class GitHubConfig:
    """GitHub configuration"""
    token: str
    repo_owner: str = "Me10101-01"
    repo_name: str = "Sovereignty-Architecture-Elevator-Pitch-"
    
    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """Create configuration from environment variables"""
        token = os.environ.get("GITHUB_TOKEN", "")
        return cls(
            token=token,
            repo_owner=os.environ.get("GITHUB_REPO_OWNER", cls.repo_owner),
            repo_name=os.environ.get("GITHUB_REPO_NAME", cls.repo_name),
        )


@dataclass
class AIConfig:
    """AI service configuration"""
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "AIConfig":
        """Create configuration from environment variables"""
        return cls(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
        )


@dataclass
class SovereignPRManagerConfig:
    """Main configuration for SovereignPRManager"""
    github: GitHubConfig = field(default_factory=GitHubConfig.from_env)
    ai: AIConfig = field(default_factory=AIConfig.from_env)
    
    # PR Review settings
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS
    max_diff_size: int = DEFAULT_MAX_DIFF_SIZE
    
    # NATS messaging
    nats_url: str = DEFAULT_NATS_URL
    
    # Auto-merge settings
    auto_merge_enabled: bool = False
    require_all_reviews: bool = True
    
    @classmethod
    def from_env(cls) -> "SovereignPRManagerConfig":
        """Create configuration from environment variables"""
        return cls(
            github=GitHubConfig.from_env(),
            ai=AIConfig.from_env(),
            confidence_threshold=float(os.environ.get(
                "CONFIDENCE_THRESHOLD", str(DEFAULT_CONFIDENCE_THRESHOLD)
            )),
            poll_interval_seconds=int(os.environ.get(
                "POLL_INTERVAL_SECONDS", str(DEFAULT_POLL_INTERVAL_SECONDS)
            )),
            max_diff_size=int(os.environ.get(
                "MAX_DIFF_SIZE", str(DEFAULT_MAX_DIFF_SIZE)
            )),
            nats_url=os.environ.get("NATS_URL", DEFAULT_NATS_URL),
            auto_merge_enabled=os.environ.get(
                "AUTO_MERGE_ENABLED", "false"
            ).lower() == "true",
            require_all_reviews=os.environ.get(
                "REQUIRE_ALL_REVIEWS", "true"
            ).lower() == "true",
        )
