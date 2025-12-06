"""
PR Monitor - Detect new PRs via GitHub API and publish to NATS.

Part of SovereignPRManager v1.0
Purpose: Monitor GitHub for new PRs and publish events for processing
Philosophy: Zero-button operation for PR detection
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class PRMonitor:
    """Monitor GitHub repository for new pull requests."""

    def __init__(
        self,
        github_token: str,
        repo_name: str,
        nats_url: str = "nats://localhost:4222",
    ):
        """
        Initialize PR Monitor.

        Args:
            github_token: GitHub API token
            repo_name: Repository in format 'owner/repo'
            nats_url: NATS server URL for event publishing
        """
        self.github_token = github_token
        self.repo_name = repo_name
        self.nats_url = nats_url
        self._processed_prs: set[int] = set()
        self._nats_client = None
        self._github = None

    async def _init_github(self):
        """Initialize GitHub client lazily."""
        if self._github is None:
            try:
                from github import Github

                self._github = Github(self.github_token)
                self._repo = self._github.get_repo(self.repo_name)
            except ImportError:
                logger.error("PyGithub not installed. Run: pip install PyGithub")
                raise

    async def _init_nats(self):
        """Initialize NATS client lazily."""
        if self._nats_client is None:
            try:
                from nats.aio.client import Client as NATS

                self._nats_client = NATS()
                await self._nats_client.connect(self.nats_url)
                logger.info(f"Connected to NATS at {self.nats_url}")
            except ImportError:
                logger.warning("NATS client not installed. Events will be logged only.")
            except Exception as e:
                logger.warning(f"Could not connect to NATS: {e}. Events will be logged only.")

    async def _publish_event(self, subject: str, data: dict[str, Any]):
        """Publish event to NATS or log if NATS unavailable."""
        event_json = json.dumps(data)

        if self._nats_client:
            await self._nats_client.publish(subject, event_json.encode())
            logger.debug(f"Published to {subject}: {data}")
        else:
            logger.info(f"Event [{subject}]: {event_json}")

    def _pr_to_event(self, pr) -> dict[str, Any]:
        """Convert GitHub PR object to event dictionary."""
        return {
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "created_at": pr.created_at.isoformat(),
            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
            "url": pr.html_url,
            "diff_url": pr.diff_url,
            "state": pr.state,
            "draft": pr.draft,
            "head_sha": pr.head.sha,
            "base_branch": pr.base.ref,
            "head_branch": pr.head.ref,
            "labels": [label.name for label in pr.labels],
            "detected_at": datetime.utcnow().isoformat(),
        }

    async def get_open_prs(self) -> list[dict[str, Any]]:
        """Get all open pull requests from the repository."""
        await self._init_github()

        prs = []
        for pr in self._repo.get_pulls(state="open"):
            prs.append(self._pr_to_event(pr))

        logger.info(f"Found {len(prs)} open PRs in {self.repo_name}")
        return prs

    async def get_draft_prs(self) -> list[dict[str, Any]]:
        """Get all draft pull requests from the repository."""
        await self._init_github()

        prs = []
        for pr in self._repo.get_pulls(state="open"):
            if pr.draft:
                prs.append(self._pr_to_event(pr))

        logger.info(f"Found {len(prs)} draft PRs in {self.repo_name}")
        return prs

    async def monitor_once(self) -> list[dict[str, Any]]:
        """
        Check for new PRs once and return newly detected ones.

        Returns:
            List of newly detected PR events
        """
        await self._init_github()
        await self._init_nats()

        new_prs = []

        for pr in self._repo.get_pulls(state="open"):
            if pr.number not in self._processed_prs:
                pr_event = self._pr_to_event(pr)
                new_prs.append(pr_event)
                self._processed_prs.add(pr.number)

                # Publish event
                await self._publish_event("pr.new", pr_event)
                logger.info(f"New PR detected: #{pr.number} - {pr.title}")

        return new_prs

    async def monitor_continuous(self, interval: int = 10):
        """
        Continuously monitor for new PRs.

        Args:
            interval: Seconds between checks
        """
        logger.info(f"Starting continuous PR monitoring (interval: {interval}s)")

        while True:
            try:
                new_prs = await self.monitor_once()
                if new_prs:
                    logger.info(f"Detected {len(new_prs)} new PRs")
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")

            await asyncio.sleep(interval)

    async def close(self):
        """Clean up resources."""
        if self._nats_client:
            await self._nats_client.close()
            logger.info("NATS connection closed")


async def main():
    """Main entry point for PR monitoring."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("GITHUB_TOKEN environment variable required")
        return

    repo_name = os.getenv(
        "GITHUB_REPO", "Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
    )
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")

    monitor = PRMonitor(github_token, repo_name, nats_url)

    try:
        await monitor.monitor_continuous()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await monitor.close()


if __name__ == "__main__":
    asyncio.run(main())
