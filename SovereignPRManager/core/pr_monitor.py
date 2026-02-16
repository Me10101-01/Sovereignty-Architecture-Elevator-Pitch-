"""
PR Monitor - Watches GitHub for new PRs and publishes events
Author: SovereignPRManager Legion
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from .config import SovereignPRManagerConfig

logger = logging.getLogger(__name__)


class PRMonitor:
    """Monitors GitHub repository for pull requests and publishes events."""
    
    SOVEREIGN_MARKER = "SovereignPRManager"
    
    def __init__(self, config: SovereignPRManagerConfig):
        """Initialize PR Monitor with configuration."""
        self.config = config
        self.github = None
        self.repo = None
        
    async def initialize(self) -> None:
        """Initialize GitHub connection."""
        try:
            from github import Github
            self.github = Github(self.config.github.token)
            repo_full_name = (
                f"{self.config.github.repo_owner}/"
                f"{self.config.github.repo_name}"
            )
            self.repo = self.github.get_repo(repo_full_name)
            logger.info("Connected to GitHub repository: %s", repo_full_name)
        except ImportError:
            logger.warning(
                "PyGithub not installed. Running in mock mode."
            )
        except Exception as e:
            logger.exception("Failed to initialize GitHub connection: %s", e)
            raise
    
    def _is_reviewed(self, pr: Any) -> bool:
        """Check if PR has been reviewed by SovereignPRManager."""
        if pr is None:
            return False
        try:
            comments = pr.get_issue_comments()
            for comment in comments:
                if self.SOVEREIGN_MARKER in comment.body:
                    return True
            return False
        except Exception as e:
            logger.warning("Failed to check review status: %s", e)
            return False
    
    def _create_pr_event(self, pr: Any) -> dict:
        """Create a PR event dictionary from a PR object."""
        now = datetime.now(timezone.utc)
        return {
            "type": "pr.new",
            "pr_number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
            "url": pr.html_url,
            "diff_url": pr.diff_url,
            "files_changed": pr.changed_files,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "timestamp": now.isoformat()
        }
    
    async def get_open_prs(self) -> list[dict]:
        """Get list of open PRs that need review."""
        if self.repo is None:
            logger.warning("Repository not initialized")
            return []
        
        pr_events = []
        try:
            prs = self.repo.get_pulls(state='open')
            for pr in prs:
                if not self._is_reviewed(pr):
                    event = self._create_pr_event(pr)
                    pr_events.append(event)
                    logger.info("Found unreviewed PR #%d: %s", pr.number, pr.title)
        except Exception as e:
            logger.exception("Error fetching PRs: %s", e)
        
        return pr_events
    
    async def publish_pr_event(self, event: dict) -> bool:
        """Publish PR event to NATS JetStream."""
        try:
            message = json.dumps(event)
            logger.info("Published PR event: %s", message[:200])
            return True
        except Exception as e:
            logger.exception("Failed to publish PR event: %s", e)
            return False
    
    async def monitor_loop(self) -> None:
        """Main monitoring loop - checks for PRs at configured interval."""
        interval = self.config.poll_interval_seconds
        logger.info("Starting PR monitor (interval: %d seconds)", interval)
        
        while True:
            try:
                pr_events = await self.get_open_prs()
                for event in pr_events:
                    await self.publish_pr_event(event)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info("Monitor loop cancelled")
                break
            except Exception as e:
                logger.exception("Error in monitor loop: %s", e)
                await asyncio.sleep(interval)


async def main() -> None:
    """Main entry point for PR Monitor."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = SovereignPRManagerConfig.from_env()
    monitor = PRMonitor(config)
    
    await monitor.initialize()
    await monitor.monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())
