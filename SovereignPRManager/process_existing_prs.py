#!/usr/bin/env python3
"""
Process Existing PRs - Bulk processing script for existing PRs.

Part of SovereignPRManager v1.0
Purpose: Process all open PRs through the Legion review pipeline
Usage: python process_existing_prs.py [--dry-run] [--limit N]
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pr_monitor import PRMonitor
from legion_reviewer import LegionReviewer
from conflict_detector import ConflictDetector
from synthesis_engine import MergeDecisionEngine
from auto_merger import AutoMerger


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BulkPRProcessor:
    """Process multiple PRs through the SovereignPRManager pipeline."""

    def __init__(
        self,
        github_token: str,
        repo_name: str,
        anthropic_key: str = None,
        openai_key: str = None,
        discord_webhook: str = None,
        declaration_path: str = None,
        dry_run: bool = False,
    ):
        """
        Initialize Bulk PR Processor.

        Args:
            github_token: GitHub API token
            repo_name: Repository in format 'owner/repo'
            anthropic_key: Anthropic API key for Claude reviews
            openai_key: OpenAI API key for GPT reviews
            discord_webhook: Discord webhook for notifications
            declaration_path: Path to Technical Declaration document
            dry_run: If True, don't actually merge PRs
        """
        self.github_token = github_token
        self.repo_name = repo_name
        self.dry_run = dry_run

        # Initialize components
        self.monitor = PRMonitor(github_token, repo_name)
        self.reviewer = LegionReviewer(anthropic_key, openai_key, declaration_path)
        self.detector = ConflictDetector()
        self.decision_engine = MergeDecisionEngine()
        self.merger = AutoMerger(github_token, repo_name, discord_webhook)

    async def process_pr(self, pr_data: dict) -> dict:
        """
        Process a single PR through the full pipeline.

        Args:
            pr_data: PR information from monitor

        Returns:
            Processing result dictionary
        """
        pr_number = pr_data.get("number")
        pr_title = pr_data.get("title")

        logger.info(f"Processing PR #{pr_number}: {pr_title}")

        result = {
            "pr_number": pr_number,
            "pr_title": pr_title,
            "status": "pending",
            "reviews": None,
            "conflicts": None,
            "decision": None,
            "merge_result": None,
            "error": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # Step 1: Legion Review
            logger.info(f"  → Running Legion review for PR #{pr_number}")
            review_result = await self.reviewer.review_pr(pr_data)
            result["reviews"] = review_result

            if review_result.get("error"):
                result["status"] = "review_failed"
                result["error"] = review_result["error"]
                return result

            # Step 2: Conflict Detection
            logger.info(f"  → Checking conflicts for PR #{pr_number}")
            # Get diff for conflict detection
            diff = ""
            if pr_data.get("diff_url"):
                try:
                    diff = await self.reviewer.fetch_diff(pr_data["diff_url"])
                except Exception as e:
                    logger.warning(f"Could not fetch diff: {e}")

            conflict_report = self.detector.detect_conflicts(
                diff,
                pr_data.get("head_branch"),
                pr_data.get("base_branch"),
            )
            result["conflicts"] = {
                "has_conflicts": conflict_report.has_conflicts,
                "git_conflicts": conflict_report.git_conflicts,
                "semantic_conflicts": conflict_report.semantic_conflicts,
                "can_auto_resolve": conflict_report.can_auto_resolve,
            }

            # Step 3: Synthesis & Decision
            logger.info(f"  → Synthesizing decision for PR #{pr_number}")
            reviews = review_result.get("reviews", [])
            decision = self.decision_engine.synthesize(
                reviews,
                {
                    "has_conflicts": conflict_report.has_conflicts,
                    "can_auto_resolve": conflict_report.can_auto_resolve,
                    "git_conflicts": conflict_report.git_conflicts,
                },
            )
            result["decision"] = {
                "action": decision.action,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
            }

            # Step 4: Execute Decision
            if decision.action == "merge":
                if self.dry_run:
                    logger.info(f"  ✓ [DRY RUN] Would merge PR #{pr_number}")
                    result["status"] = "would_merge"
                else:
                    logger.info(f"  → Merging PR #{pr_number}")
                    merge_result = await self.merger.merge_pr(
                        pr_number,
                        {
                            "action": decision.action,
                            "confidence": decision.confidence,
                            "reasoning": decision.reasoning,
                            "reviews_summary": review_result.get("summary", {}),
                        },
                    )
                    result["merge_result"] = {
                        "success": merge_result.success,
                        "merge_sha": merge_result.merge_sha,
                        "error": merge_result.error,
                    }
                    result["status"] = "merged" if merge_result.success else "merge_failed"
            elif decision.action == "reject":
                result["status"] = "rejected"
                logger.info(f"  ✗ PR #{pr_number} rejected: {decision.reasoning}")
            else:
                result["status"] = "review_required"
                logger.info(f"  ⚠ PR #{pr_number} requires human review")

        except Exception as e:
            logger.error(f"Error processing PR #{pr_number}: {e}")
            result["status"] = "error"
            result["error"] = str(e)

        return result

    async def process_all(self, limit: int = None, drafts_only: bool = False) -> dict:
        """
        Process all open PRs.

        Args:
            limit: Maximum number of PRs to process
            drafts_only: Only process draft PRs

        Returns:
            Summary report of all processing
        """
        logger.info(f"Starting bulk PR processing for {self.repo_name}")
        logger.info(f"Dry run: {self.dry_run}")

        # Get PRs
        if drafts_only:
            prs = await self.monitor.get_draft_prs()
        else:
            prs = await self.monitor.get_open_prs()

        if limit:
            prs = prs[:limit]

        logger.info(f"Found {len(prs)} PRs to process")

        results = []
        for i, pr in enumerate(prs, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing PR {i}/{len(prs)}")
            logger.info(f"{'='*50}")

            result = await self.process_pr(pr)
            results.append(result)

            # Rate limiting: 10 seconds between PRs
            if i < len(prs):
                logger.info("Rate limiting: waiting 10 seconds...")
                await asyncio.sleep(10)

        # Generate summary report
        report = self._generate_report(results)

        return report

    def _generate_report(self, results: list) -> dict:
        """Generate summary report from processing results."""
        total = len(results)
        status_counts = {}

        for result in results:
            status = result.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        report = {
            "summary": {
                "total_prs": total,
                "merged": status_counts.get("merged", 0) + status_counts.get("would_merge", 0),
                "rejected": status_counts.get("rejected", 0),
                "requires_review": status_counts.get("review_required", 0),
                "errors": status_counts.get("error", 0) + status_counts.get("review_failed", 0),
            },
            "status_breakdown": status_counts,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
            "dry_run": self.dry_run,
        }

        return report


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process existing PRs through SovereignPRManager"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually merge, just show what would happen",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of PRs to process",
    )
    parser.add_argument(
        "--drafts-only",
        action="store_true",
        help="Only process draft PRs",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="pr_processing_report.json",
        help="Output file for processing report",
    )

    args = parser.parse_args()

    # Get configuration from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("GITHUB_TOKEN environment variable required")
        sys.exit(1)

    repo_name = os.getenv(
        "GITHUB_REPO", "Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
    )
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    declaration_path = os.getenv("DECLARATION_PATH")

    if not anthropic_key and not openai_key:
        logger.warning(
            "No AI API keys configured. Reviews will be limited. "
            "Set ANTHROPIC_API_KEY or OPENAI_API_KEY."
        )

    # Initialize processor
    processor = BulkPRProcessor(
        github_token=github_token,
        repo_name=repo_name,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        discord_webhook=discord_webhook,
        declaration_path=declaration_path,
        dry_run=args.dry_run,
    )

    # Process PRs
    report = await processor.process_all(
        limit=args.limit,
        drafts_only=args.drafts_only,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("📊 BULK PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total PRs: {report['summary']['total_prs']}")
    print(f"Merged: {report['summary']['merged']}")
    print(f"Rejected: {report['summary']['rejected']}")
    print(f"Requires review: {report['summary']['requires_review']}")
    print(f"Errors: {report['summary']['errors']}")
    print(f"\nDry run: {report['dry_run']}")

    # Save report
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
