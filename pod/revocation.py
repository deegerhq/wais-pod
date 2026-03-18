"""
PoD Token Revocation List.

Used by agent platforms to publish revoked tokens
and by websites to check revocation status.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


# Valid revocation reasons.
REASON_USER_REVOKED = "user_revoked"
REASON_PLATFORM_REVOKED = "platform_revoked"
REASON_COMPROMISED = "compromised"
REASON_SUPERSEDED = "superseded"

VALID_REASONS = {
    REASON_USER_REVOKED,
    REASON_PLATFORM_REVOKED,
    REASON_COMPROMISED,
    REASON_SUPERSEDED,
}

# TTL bounds in seconds.
MIN_TTL_SECONDS = 60
MAX_TTL_SECONDS = 300


@dataclass
class RevocationEntry:
    """A single revoked token entry."""

    jti: str
    revoked_at: int
    reason: str

    def __post_init__(self) -> None:
        if self.reason not in VALID_REASONS:
            raise ValueError(
                f"Invalid reason '{self.reason}'. Must be one of: {sorted(VALID_REASONS)}"
            )

    def to_dict(self) -> dict:
        return {
            "jti": self.jti,
            "revoked_at": self.revoked_at,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> RevocationEntry:
        return cls(
            jti=data["jti"],
            revoked_at=data["revoked_at"],
            reason=data["reason"],
        )


@dataclass
class RevocationList:
    """
    A list of revoked PoD tokens published by an agent platform.

    Platforms publish this at /.well-known/wais-revocation.
    Websites fetch and cache it to check token revocation status.
    """

    issuer: str
    ttl_seconds: int = 300
    entries: list[RevocationEntry] = field(default_factory=list)
    published_at: int = 0
    version: int = 1

    def __post_init__(self) -> None:
        # Clamp TTL to valid range.
        if self.ttl_seconds < MIN_TTL_SECONDS:
            self.ttl_seconds = MIN_TTL_SECONDS
        elif self.ttl_seconds > MAX_TTL_SECONDS:
            self.ttl_seconds = MAX_TTL_SECONDS
        if self.published_at == 0:
            self.published_at = int(time.time())
        # Build index for fast lookup.
        self._index: dict[str, RevocationEntry] = {e.jti: e for e in self.entries}

    def revoke(self, jti: str, reason: str, revoked_at: Optional[int] = None) -> RevocationEntry:
        """Add a token to the revocation list."""
        entry = RevocationEntry(
            jti=jti,
            revoked_at=revoked_at or int(time.time()),
            reason=reason,
        )
        self.entries.append(entry)
        self._index[jti] = entry
        return entry

    def is_revoked(self, jti: str) -> Optional[RevocationEntry]:
        """Check if a token is revoked. Returns the entry if found, None otherwise."""
        return self._index.get(jti)

    def prune(self, max_token_exp: int) -> int:
        """Remove entries for tokens that expired before max_token_exp.

        Since revoked_at is always <= exp, entries with revoked_at < max_token_exp
        are for tokens that have naturally expired and no longer need tracking.

        Returns the number of entries removed.
        """
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.revoked_at >= max_token_exp]
        self._index = {e.jti: e for e in self.entries}
        return before - len(self.entries)

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "version": self.version,
            "issuer": self.issuer,
            "published_at": self.published_at,
            "ttl_seconds": self.ttl_seconds,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict) -> RevocationList:
        """Deserialize from a JSON-compatible dict."""
        entries = [RevocationEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(
            issuer=data["issuer"],
            ttl_seconds=data.get("ttl_seconds", 300),
            entries=entries,
            published_at=data.get("published_at", 0),
            version=data.get("version", 1),
        )
