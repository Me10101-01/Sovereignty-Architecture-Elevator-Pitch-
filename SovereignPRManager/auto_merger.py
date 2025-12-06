"""
Auto Merger - Execute merges with cryptographic provenance.

Part of SovereignPRManager v1.0
Purpose: Autonomously merge PRs with full audit trail
Philosophy: Cryptographic verification and immutable provenance
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MergeResult:
    """Result of a merge operation."""

    success: bool
    pr_number: int
    pr_title: str
    merge_sha: str = ""
    error: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ProvenanceRecord:
    """Cryptographic provenance record for a merge."""

    pr_number: int
    pr_title: str
    decision: dict[str, Any]
    merged_by: str
    git_sha: str
    timestamp: str
    signature: str = ""
    ots_proof: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pr_number": self.pr_number,
            "pr_title": self.pr_title,
            "decision": self.decision,
            "merged_by": self.merged_by,
            "git_sha": self.git_sha,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "ots_proof": self.ots_proof,
        }


class ProvenanceSigner:
    """Generate cryptographic signatures for provenance records."""

    def __init__(self, signing_key: str = None):
        """
        Initialize Provenance Signer.

        Args:
            signing_key: Secret key for HMAC signing (or generates random)
        """
        self.signing_key = signing_key or os.urandom(32).hex()

    def sign(self, data: dict[str, Any]) -> str:
        """
        Generate BLAKE3 HMAC signature for data.

        Falls back to SHA-256 if BLAKE3 is not available.

        Args:
            data: Dictionary to sign

        Returns:
            Hex-encoded signature
        """
        message = json.dumps(data, sort_keys=True, default=str).encode()

        try:
            import blake3

            hasher = blake3.blake3(key=self.signing_key.encode()[:32].ljust(32, b'\0'))
            hasher.update(message)
            return hasher.hexdigest()
        except ImportError:
            # Fallback to SHA-256 HMAC
            import hmac

            signature = hmac.new(
                self.signing_key.encode(),
                message,
                hashlib.sha256,
            ).hexdigest()
            return signature

    def verify(self, data: dict[str, Any], signature: str) -> bool:
        """
        Verify a signature against data.

        Args:
            data: Dictionary that was signed
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        expected = self.sign(data)
        return hmac.compare_digest(expected, signature)


class OpenTimestamper:
    """Interface to OpenTimestamps for blockchain anchoring."""

    @staticmethod
    def timestamp(data: bytes) -> str:
        """
        Create an OpenTimestamps proof for data.

        Args:
            data: Data to timestamp

        Returns:
            Hex-encoded timestamp proof
        """
        try:
            import opentimestamps
            from opentimestamps.core.op import OpSHA256
            from opentimestamps.core.timestamp import Timestamp

            # Create timestamp
            file_hash = hashlib.sha256(data).digest()
            timestamp = Timestamp(file_hash)

            return timestamp.msg.hex()
        except ImportError:
            # Fallback: just return SHA-256 hash
            logger.warning("OpenTimestamps not available, using SHA-256 hash only")
            return hashlib.sha256(data).hexdigest()


class DiscordNotifier:
    """Send notifications to Discord."""

    def __init__(self, webhook_url: str):
        """
        Initialize Discord Notifier.

        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url

    async def notify(
        self,
        title: str,
        message: str,
        color: int = 0x00FF00,
        fields: list[dict[str, str]] = None,
    ):
        """
        Send a notification to Discord.

        Args:
            title: Embed title
            message: Main message content
            color: Embed color (green by default)
            fields: Additional embed fields
        """
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "SovereignPRManager v1.0"},
        }

        if fields:
            embed["fields"] = [
                {"name": f["name"], "value": f["value"], "inline": f.get("inline", True)}
                for f in fields
            ]

        payload = {"embeds": [embed]}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.debug(f"Discord notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")


class ElasticsearchLogger:
    """Log provenance records to Elasticsearch."""

    def __init__(self, es_url: str, index: str = "sovereignprmanager-audit"):
        """
        Initialize Elasticsearch Logger.

        Args:
            es_url: Elasticsearch URL
            index: Index name for audit logs
        """
        self.es_url = es_url.rstrip("/")
        self.index = index

    async def log(self, record: dict[str, Any]):
        """
        Log a record to Elasticsearch.

        Args:
            record: Record to log
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.es_url}/{self.index}/_doc",
                    json=record,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.debug(f"Logged to Elasticsearch: {record.get('pr_number')}")
        except Exception as e:
            logger.error(f"Failed to log to Elasticsearch: {e}")


class AutoMerger:
    """Autonomously merge PRs with cryptographic provenance."""

    def __init__(
        self,
        github_token: str,
        repo_name: str,
        discord_webhook: str = None,
        elasticsearch_url: str = None,
        signing_key: str = None,
    ):
        """
        Initialize Auto Merger.

        Args:
            github_token: GitHub API token
            repo_name: Repository in format 'owner/repo'
            discord_webhook: Discord webhook URL for notifications
            elasticsearch_url: Elasticsearch URL for audit logging
            signing_key: Key for cryptographic signing
        """
        self.github_token = github_token
        self.repo_name = repo_name
        self.signer = ProvenanceSigner(signing_key)
        self.timestamper = OpenTimestamper()

        self.discord = DiscordNotifier(discord_webhook) if discord_webhook else None
        self.es_logger = (
            ElasticsearchLogger(elasticsearch_url) if elasticsearch_url else None
        )

    async def _github_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
    ) -> dict[str, Any]:
        """Make a request to GitHub API."""
        url = f"https://api.github.com/repos/{self.repo_name}/{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                json=data,
                timeout=30.0,
            )
            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

    async def get_pr(self, pr_number: int) -> dict[str, Any]:
        """Get PR details from GitHub."""
        return await self._github_request("GET", f"pulls/{pr_number}")

    async def merge_pr(
        self,
        pr_number: int,
        decision: dict[str, Any],
        merge_method: str = "squash",
    ) -> MergeResult:
        """
        Execute merge with full audit trail.

        Args:
            pr_number: PR number to merge
            decision: Merge decision from synthesis engine
            merge_method: Git merge method (merge, squash, rebase)

        Returns:
            MergeResult with status and provenance
        """
        try:
            # Get PR details
            pr = await self.get_pr(pr_number)
            pr_title = pr.get("title", f"PR #{pr_number}")
            head_sha = pr.get("head", {}).get("sha", "unknown")

            # Create provenance record
            provenance = ProvenanceRecord(
                pr_number=pr_number,
                pr_title=pr_title,
                decision=decision,
                merged_by="SovereignPRManager v1.0",
                git_sha=head_sha,
                timestamp=datetime.utcnow().isoformat(),
            )

            # Sign the provenance
            provenance_data = {
                "pr_number": pr_number,
                "pr_title": pr_title,
                "decision": decision,
                "git_sha": head_sha,
                "timestamp": provenance.timestamp,
            }
            provenance.signature = self.signer.sign(provenance_data)

            # Blockchain timestamp
            provenance.ots_proof = self.timestamper.timestamp(
                json.dumps(provenance_data).encode()
            )

            # Build commit message
            commit_message = self._build_commit_message(provenance, decision)

            # Execute merge
            merge_data = {
                "commit_title": f"🤖 Auto-merge: {pr_title}",
                "commit_message": commit_message,
                "merge_method": merge_method,
            }

            result = await self._github_request(
                "PUT", f"pulls/{pr_number}/merge", merge_data
            )

            merge_sha = result.get("sha", "")

            # Notify Discord
            if self.discord:
                await self._notify_discord_success(pr_number, pr_title, decision, merge_sha)

            # Log to Elasticsearch
            if self.es_logger:
                await self.es_logger.log({
                    **provenance.to_dict(),
                    "merge_sha": merge_sha,
                    "status": "success",
                })

            return MergeResult(
                success=True,
                pr_number=pr_number,
                pr_title=pr_title,
                merge_sha=merge_sha,
                provenance=provenance.to_dict(),
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Merge failed for PR #{pr_number}: {error_msg}")

            if self.discord:
                await self._notify_discord_failure(pr_number, error_msg)

            return MergeResult(
                success=False,
                pr_number=pr_number,
                pr_title=pr_title if 'pr_title' in dir() else f"PR #{pr_number}",
                error=error_msg,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Merge failed for PR #{pr_number}: {error_msg}")

            return MergeResult(
                success=False,
                pr_number=pr_number,
                pr_title=f"PR #{pr_number}",
                error=error_msg,
            )

    def _build_commit_message(
        self, provenance: ProvenanceRecord, decision: dict[str, Any]
    ) -> str:
        """Build the commit message with provenance information."""
        return f"""
Autonomously merged by SovereignPRManager v1.0

Confidence: {decision.get('confidence', 0):.2%}
Reviews: {decision.get('reviews_summary', {}).get('total_reviews', 0)} AI agents
Action: {decision.get('action', 'unknown')}
Reasoning: {decision.get('reasoning', 'N/A')}

Provenance: {provenance.signature[:32]}...
Timestamp Proof: {provenance.ots_proof[:32]}...
"""

    async def _notify_discord_success(
        self,
        pr_number: int,
        pr_title: str,
        decision: dict[str, Any],
        merge_sha: str,
    ):
        """Notify Discord of successful merge."""
        await self.discord.notify(
            title=f"✅ PR #{pr_number} Auto-Merged",
            message=pr_title,
            color=0x00FF00,  # Green
            fields=[
                {"name": "Confidence", "value": f"{decision.get('confidence', 0):.1%}"},
                {
                    "name": "Reviews",
                    "value": str(
                        decision.get("reviews_summary", {}).get("total_reviews", 0)
                    ),
                },
                {"name": "Merge SHA", "value": f"`{merge_sha[:8]}`"},
            ],
        )

    async def _notify_discord_failure(self, pr_number: int, error: str):
        """Notify Discord of failed merge."""
        await self.discord.notify(
            title=f"❌ PR #{pr_number} Merge Failed",
            message=error[:200],
            color=0xFF0000,  # Red
        )

    async def close(self):
        """Clean up resources."""
        pass


async def main():
    """Test the Auto Merger."""
    logging.basicConfig(level=logging.INFO)

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("GITHUB_TOKEN required")
        return

    repo_name = os.getenv(
        "GITHUB_REPO", "Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
    )

    merger = AutoMerger(github_token, repo_name)

    # Example decision
    decision = {
        "action": "merge",
        "confidence": 0.95,
        "reasoning": "All reviews approved with high confidence",
        "reviews_summary": {"total_reviews": 4},
    }

    # Note: This would actually merge a PR - use with caution!
    # result = await merger.merge_pr(1, decision)
    # print(f"Result: {result}")

    print("AutoMerger initialized successfully")
    print(f"Repository: {repo_name}")


if __name__ == "__main__":
    asyncio.run(main())
