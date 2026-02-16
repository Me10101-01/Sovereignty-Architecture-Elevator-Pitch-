"""
PR Monitor: Detects new PRs and processes them through the review pipeline.
"""

import asyncio
import logging
from typing import Optional

from .config import Config
from .models import PRData, utcnow

try:
    from github import Github
    from github.PullRequest import PullRequest

    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False
    Github = None
    PullRequest = None

logger = logging.getLogger(__name__)


class PRMonitor:
    """Monitor GitHub for new PRs and publish events."""

    def __init__(self, config: Config):
        """Initialize the PR monitor."""
        self.config = config
        self._github: Optional[Github] = None
        self._processed_prs: set[int] = set()

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

    def get_open_prs(self) -> list[PRData]:
        """Fetch all open PRs from the repository."""
        try:
            repo = self.github.get_repo(self.config.github.repo)
            prs = repo.get_pulls(state="open")

            pr_list = []
            for pr in prs:
                pr_data = self._convert_pr(pr)
                pr_list.append(pr_data)

            return pr_list
        except Exception as e:
            logger.error(f"Failed to fetch PRs: {e}")
            return []

    def get_unprocessed_prs(self) -> list[PRData]:
        """Get PRs that haven't been processed yet."""
        all_prs = self.get_open_prs()
        return [pr for pr in all_prs if pr.number not in self._processed_prs]

    def get_draft_prs(self) -> list[PRData]:
        """Get all draft PRs that need review."""
        all_prs = self.get_open_prs()
        return [pr for pr in all_prs if pr.is_draft]

    def mark_processed(self, pr_number: int) -> None:
        """Mark a PR as processed."""
        self._processed_prs.add(pr_number)

    def reset_processed(self) -> None:
        """Reset the processed PR tracking."""
        self._processed_prs.clear()

    def _convert_pr(self, pr: "PullRequest") -> PRData:
        """Convert GitHub PR object to our data model."""
        return PRData(
            number=pr.number,
            title=pr.title,
            author=pr.user.login if pr.user else "unknown",
            created_at=pr.created_at or utcnow(),
            url=pr.html_url,
            diff_url=pr.diff_url,
            head_sha=pr.head.sha if pr.head else "",
            base_branch=pr.base.ref if pr.base else "main",
            is_draft=pr.draft,
            labels=[label.name for label in pr.labels],
        )

    def get_pr_diff(self, pr_number: int) -> str:
        """Fetch the diff for a specific PR."""
        try:
            repo = self.github.get_repo(self.config.github.repo)
            pr = repo.get_pull(pr_number)

            # Get files changed
            files = pr.get_files()
            diff_content = []

            for file in files:
                diff_content.append(f"--- a/{file.filename}")
                diff_content.append(f"+++ b/{file.filename}")
                if file.patch:
                    diff_content.append(file.patch)
                diff_content.append("")

            return "\n".join(diff_content)
        except Exception as e:
            logger.error(f"Failed to get diff for PR #{pr_number}: {e}")
            return ""


async def monitor_prs(config: Config, callback) -> None:
    """
    Continuously monitor for new PRs.

    Args:
        config: Configuration object
        callback: Async function to call for each new PR
    """
    monitor = PRMonitor(config)
    logger.info(f"Starting PR monitor for {config.github.repo}")
    logger.info(f"Poll interval: {config.poll_interval_seconds} seconds")

    while True:
        try:
            prs = monitor.get_unprocessed_prs()
            for pr in prs:
                if pr.is_draft:
                    logger.info(f"Processing draft PR #{pr.number}: {pr.title}")
                    await callback(pr, monitor)
                    monitor.mark_processed(pr.number)

            await asyncio.sleep(config.poll_interval_seconds)
        except KeyboardInterrupt:
            logger.info("PR monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in PR monitor loop: {e}")
            await asyncio.sleep(config.poll_interval_seconds)
