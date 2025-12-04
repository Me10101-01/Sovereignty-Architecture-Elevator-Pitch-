"""
Configuration management for SovereignPRManager.

Handles environment variables, thresholds, and integration settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MergeThresholds:
    """Confidence thresholds for merge decisions."""

    auto_merge: float = 0.90  # 90% confidence required for auto-merge
    security_veto: float = 0.80  # Security review below 80% blocks merge
    sovereignty_minimum: float = 0.70  # Must meet 70% sovereignty standards


@dataclass
class GitHubConfig:
    """GitHub integration configuration."""

    token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    repo: str = "Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
    org: str = "Strategickhaos-Swarm-Intelligence"

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        return bool(self.token)


@dataclass
class DiscordConfig:
    """Discord notification configuration."""

    webhook_url: str = field(
        default_factory=lambda: os.getenv("DISCORD_WEBHOOK_URL", "")
    )
    pr_notifications_channel: str = "#pr-automation"
    human_review_channel: str = "#requires-human"

    @property
    def enabled(self) -> bool:
        """Check if Discord notifications are enabled."""
        return bool(self.webhook_url)


@dataclass
class Config:
    """Main configuration for SovereignPRManager."""

    github: GitHubConfig = field(default_factory=GitHubConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    thresholds: MergeThresholds = field(default_factory=MergeThresholds)
    declaration_path: Optional[str] = None
    enforce_declaration: bool = True
    poll_interval_seconds: int = 10
    dry_run: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            github=GitHubConfig(
                token=os.getenv("GITHUB_TOKEN", ""),
                repo=os.getenv(
                    "GITHUB_REPO", "Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
                ),
                org=os.getenv("GITHUB_ORG", "Strategickhaos-Swarm-Intelligence"),
            ),
            discord=DiscordConfig(
                webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
            ),
            thresholds=MergeThresholds(
                auto_merge=float(os.getenv("MERGE_THRESHOLD_AUTO", "0.90")),
                security_veto=float(os.getenv("MERGE_THRESHOLD_SECURITY", "0.80")),
                sovereignty_minimum=float(
                    os.getenv("MERGE_THRESHOLD_SOVEREIGNTY", "0.70")
                ),
            ),
            declaration_path=os.getenv("DECLARATION_PATH"),
            enforce_declaration=os.getenv("ENFORCE_DECLARATION", "true").lower()
            == "true",
            poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "10")),
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        )

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not self.github.validate():
            errors.append("GITHUB_TOKEN is required")
        return errors
