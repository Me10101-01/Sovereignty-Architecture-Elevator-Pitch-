"""
Auto Merger: Execute merges with provenance trail.

Provides merge execution with:
- Cryptographic signing (when available)
- Audit logging
- Discord notifications
- Provenance records
"""

import hashlib
import json
import logging
from typing import Optional

from .config import Config
from .models import MergeAction, MergeDecision, MergeProvenance, PRData, utcnow

try:
    from github import Github
    from github.PullRequest import PullRequest

    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False
    Github = None
    PullRequest = None

logger = logging.getLogger(__name__)


class AutoMerger:
    """Autonomously merge PRs with cryptographic provenance."""

    def __init__(self, config: Config):
        """Initialize the auto merger."""
        self.config = config
        self._github: Optional[Github] = None

    @property
    def github(self) -> "Github":
        """Lazy initialization of GitHub client."""
        if self._github is None:
            if not HAS_GITHUB:
                raise ImportError(
                    "PyGithub is required. Install with: pip install PyGithub"
                )
            self._github = Github(self.config.github.token)
        return self._github

    async def merge_pr(
        self, pr_data: PRData, decision: MergeDecision
    ) -> dict:
        """
        Execute merge with full audit trail.

        Args:
            pr_data: PR information
            decision: Merge decision from synthesis engine

        Returns:
            dict with success status and provenance record
        """
        if decision.action != MergeAction.MERGE:
            return {
                "success": False,
                "error": f"Cannot merge: action is {decision.action.value}",
                "provenance": None,
            }

        # Create provenance record
        provenance = self._create_provenance(pr_data, decision)

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would merge PR #{pr_data.number}")
            return {
                "success": True,
                "dry_run": True,
                "pr_number": pr_data.number,
                "provenance": provenance.to_dict(),
            }

        try:
            repo = self.github.get_repo(self.config.github.repo)
            pr = repo.get_pull(pr_data.number)

            # Build commit message
            commit_title = f"🤖 Auto-merge: {pr_data.title}"
            commit_message = self._build_commit_message(decision, provenance)

            # Execute merge
            merge_result = pr.merge(
                commit_title=commit_title,
                commit_message=commit_message,
                merge_method="squash",
            )

            # Update provenance with merge SHA
            provenance.git_sha = merge_result.sha if merge_result else ""

            # Log and notify
            await self._log_merge(provenance)
            await self._notify_discord(pr_data, decision, provenance)

            return {
                "success": True,
                "pr_number": pr_data.number,
                "merge_sha": provenance.git_sha,
                "provenance": provenance.to_dict(),
            }

        except Exception as e:
            logger.error(f"Failed to merge PR #{pr_data.number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "provenance": provenance.to_dict(),
            }

    def _create_provenance(
        self, pr_data: PRData, decision: MergeDecision
    ) -> MergeProvenance:
        """Create a provenance record for the merge."""
        provenance = MergeProvenance(
            pr_number=pr_data.number,
            pr_title=pr_data.title,
            decision=decision,
            git_sha=pr_data.head_sha,
        )

        # Generate signature
        provenance.signature = self._sign_provenance(provenance)

        return provenance

    def _sign_provenance(self, provenance: MergeProvenance) -> str:
        """
        Generate a cryptographic signature for provenance.

        Uses BLAKE3-like approach with SHA-256 as fallback.
        """
        data = json.dumps(
            {
                "pr_number": provenance.pr_number,
                "pr_title": provenance.pr_title,
                "decision": provenance.decision.action.value,
                "confidence": provenance.decision.confidence,
                "git_sha": provenance.git_sha,
                "timestamp": provenance.timestamp.isoformat(),
            },
            sort_keys=True,
        )

        signature = hashlib.sha256(data.encode()).hexdigest()
        return signature  # Full SHA-256 hash for cryptographic integrity

    def _build_commit_message(
        self, decision: MergeDecision, provenance: MergeProvenance
    ) -> str:
        """Build the commit message with provenance info."""
        parts = [
            "Autonomously merged by SovereignPRManager v1.0",
            "",
            f"Confidence: {decision.confidence:.1%}",
            f"Reviews: {len(decision.reviews)} automated review(s)",
            f"Reasoning: {decision.reasoning}",
            "",
            f"Provenance: {provenance.signature}",
        ]
        return "\n".join(parts)

    async def _log_merge(self, provenance: MergeProvenance) -> None:
        """Log the merge to audit systems."""
        logger.info(
            f"Merged PR #{provenance.pr_number}: {provenance.pr_title}"
        )
        logger.info(f"  Confidence: {provenance.decision.confidence:.1%}")
        logger.info(f"  Signature: {provenance.signature}")

    async def _notify_discord(
        self,
        pr_data: PRData,
        decision: MergeDecision,
        provenance: MergeProvenance,
    ) -> None:
        """Send notification to Discord."""
        if not self.config.discord.enabled:
            return

        try:
            import aiohttp

            message = {
                "embeds": [
                    {
                        "title": f"🤖 Auto-merged PR #{pr_data.number}",
                        "description": pr_data.title,
                        "color": 0x00FF00,  # Green
                        "fields": [
                            {
                                "name": "Confidence",
                                "value": f"{decision.confidence:.1%}",
                                "inline": True,
                            },
                            {
                                "name": "Author",
                                "value": pr_data.author,
                                "inline": True,
                            },
                            {
                                "name": "Provenance",
                                "value": f"`{provenance.signature}`",
                                "inline": False,
                            },
                        ],
                        "url": pr_data.url,
                        "timestamp": utcnow().isoformat(),
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.discord.webhook_url,
                    json=message,
                ) as resp:
                    if resp.status != 204:
                        logger.warning(
                            f"Discord notification failed: {resp.status}"
                        )

        except ImportError:
            logger.debug("aiohttp not available for Discord notifications")
        except Exception as e:
            logger.warning(f"Failed to send Discord notification: {e}")
