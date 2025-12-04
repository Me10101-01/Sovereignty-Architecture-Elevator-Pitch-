"""
SovereignPRManager: Main entry point and orchestrator.

Usage:
    # Process all open PRs (dry run)
    python -m sovereign_pr_manager --dry-run

    # Process all open PRs
    python -m sovereign_pr_manager

    # Continuous monitoring
    python -m sovereign_pr_manager --monitor
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime

from .auto_merger import AutoMerger
from .config import Config
from .conflict_detector import ConflictDetector
from .models import MergeAction, PRData
from .pr_monitor import PRMonitor
from .reviewer import CodeReviewer
from .synthesis_engine import SynthesisEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sovereign_pr_manager")


class SovereignPRManager:
    """
    Main orchestrator for autonomous PR management.

    Coordinates:
    - PR monitoring
    - Code review
    - Conflict detection
    - Dialectical synthesis
    - Auto-merge with provenance
    """

    def __init__(self, config: Config):
        """Initialize the PR manager."""
        self.config = config
        self.monitor = PRMonitor(config)
        self.reviewer = CodeReviewer(config)
        self.conflict_detector = ConflictDetector()
        self.synthesis_engine = SynthesisEngine(config)
        self.auto_merger = AutoMerger(config)

    async def process_pr(self, pr_data: PRData) -> dict:
        """
        Process a single PR through the full pipeline.

        Pipeline stages:
        1. Fetch diff
        2. Run reviews
        3. Detect conflicts
        4. Synthesize decision
        5. Execute merge (if approved)
        """
        logger.info(f"Processing PR #{pr_data.number}: {pr_data.title}")

        # Stage 1: Fetch diff
        diff = self.monitor.get_pr_diff(pr_data.number)
        if not diff:
            logger.warning(f"No diff available for PR #{pr_data.number}")
            return {"pr_number": pr_data.number, "error": "No diff available"}

        # Stage 2: Run reviews
        logger.info("  Running automated reviews...")
        reviews = await self.reviewer.review_pr(pr_data, diff)
        for review in reviews:
            status = "✓" if review.approve else "✗"
            logger.info(
                f"    {status} {review.review_type.value}: "
                f"{review.confidence:.1%} confidence"
            )

        # Stage 3: Detect conflicts
        logger.info("  Checking for conflicts...")
        conflicts = self.conflict_detector.detect_conflicts(diff)
        if conflicts.has_conflicts:
            logger.info("    ⚠ Conflicts detected")

        # Stage 4: Synthesize decision
        logger.info("  Synthesizing decision...")
        decision = self.synthesis_engine.synthesize(reviews, conflicts)
        logger.info(
            f"    Decision: {decision.action.value} "
            f"({decision.confidence:.1%})"
        )

        # Stage 5: Execute merge
        result = {
            "pr_number": pr_data.number,
            "title": pr_data.title,
            "decision": decision.to_dict(),
            "merged": False,
        }

        if decision.action == MergeAction.MERGE:
            logger.info("  Executing merge...")
            merge_result = await self.auto_merger.merge_pr(pr_data, decision)
            result["merged"] = merge_result.get("success", False)
            result["merge_result"] = merge_result
        else:
            logger.info(f"  Skipping merge: {decision.reasoning}")

        return result

    async def process_all_open_prs(self) -> dict:
        """Process all open PRs in the repository."""
        logger.info("=" * 60)
        logger.info("SovereignPRManager: Processing all open PRs")
        logger.info("=" * 60)

        prs = self.monitor.get_open_prs()
        logger.info(f"Found {len(prs)} open PR(s)")

        results = []
        merged_count = 0
        review_required_count = 0
        blocked_count = 0

        for pr in prs:
            try:
                result = await self.process_pr(pr)
                results.append(result)

                action = result.get("decision", {}).get("action", "unknown")
                if action == "merge" and result.get("merged"):
                    merged_count += 1
                elif action == "review_required":
                    review_required_count += 1
                elif action == "blocked":
                    blocked_count += 1

                # Rate limit: avoid API throttling
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error processing PR #{pr.number}: {e}")
                results.append({"pr_number": pr.number, "error": str(e)})

        # Generate summary
        summary = {
            "total_prs": len(prs),
            "processed": len(results),
            "auto_merged": merged_count,
            "requires_review": review_required_count,
            "blocked": blocked_count,
            "timestamp": datetime.utcnow().isoformat(),
            "dry_run": self.config.dry_run,
        }

        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total PRs: {summary['total_prs']}")
        logger.info(f"Auto-merged: {summary['auto_merged']}")
        logger.info(f"Requires review: {summary['requires_review']}")
        logger.info(f"Blocked: {summary['blocked']}")
        if summary["dry_run"]:
            logger.info("(DRY RUN - no actual merges performed)")
        logger.info("=" * 60)

        return summary


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SovereignPRManager: Autonomous PR Orchestration System"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually merging PRs",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Run in continuous monitoring mode",
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="Process a specific PR number",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = Config.from_env()
    if args.dry_run:
        config.dry_run = True

    # Validate configuration
    errors = config.validate()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Create manager
    manager = SovereignPRManager(config)

    if args.pr:
        # Process specific PR
        prs = manager.monitor.get_open_prs()
        pr = next((p for p in prs if p.number == args.pr), None)
        if pr:
            result = await manager.process_pr(pr)
            print(f"Result: {result}")
        else:
            logger.error(f"PR #{args.pr} not found")
            sys.exit(1)
    elif args.monitor:
        # Continuous monitoring mode
        logger.info("Starting continuous monitoring mode...")
        from .pr_monitor import monitor_prs

        async def callback(pr, monitor):
            await manager.process_pr(pr)

        await monitor_prs(config, callback)
    else:
        # Process all open PRs
        summary = await manager.process_all_open_prs()
        return summary


if __name__ == "__main__":
    asyncio.run(main())
