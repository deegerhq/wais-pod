"""Tests for PoD token revocation mechanism."""

import time

import pytest

from pod.revocation import (
    RevocationEntry,
    RevocationList,
    REASON_USER_REVOKED,
    REASON_PLATFORM_REVOKED,
    REASON_COMPROMISED,
    REASON_SUPERSEDED,
    MIN_TTL_SECONDS,
    MAX_TTL_SECONDS,
)
from pod.scopes import Scopes
from tests.conftest import AUDIENCE


# --- RevocationEntry tests ---


class TestRevocationEntry:
    def test_create_valid_entry(self):
        entry = RevocationEntry(jti="token-1", revoked_at=1000, reason=REASON_USER_REVOKED)
        assert entry.jti == "token-1"
        assert entry.revoked_at == 1000
        assert entry.reason == REASON_USER_REVOKED

    def test_all_valid_reasons(self):
        for reason in [REASON_USER_REVOKED, REASON_PLATFORM_REVOKED, REASON_COMPROMISED, REASON_SUPERSEDED]:
            entry = RevocationEntry(jti="t", revoked_at=1, reason=reason)
            assert entry.reason == reason

    def test_invalid_reason_raises(self):
        with pytest.raises(ValueError, match="Invalid reason"):
            RevocationEntry(jti="t", revoked_at=1, reason="bad_reason")

    def test_entry_to_dict(self):
        entry = RevocationEntry(jti="abc", revoked_at=500, reason=REASON_COMPROMISED)
        d = entry.to_dict()
        assert d == {"jti": "abc", "revoked_at": 500, "reason": "compromised"}

    def test_entry_from_dict(self):
        entry = RevocationEntry.from_dict({"jti": "x", "revoked_at": 99, "reason": "superseded"})
        assert entry.jti == "x"
        assert entry.revoked_at == 99
        assert entry.reason == REASON_SUPERSEDED


# --- RevocationList tests ---


class TestRevocationList:
    def test_create_empty_list(self):
        rl = RevocationList(issuer="https://platform.com")
        assert rl.issuer == "https://platform.com"
        assert rl.version == 1
        assert rl.entries == []
        assert rl.ttl_seconds == MAX_TTL_SECONDS

    def test_ttl_clamp_below_min(self):
        rl = RevocationList(issuer="https://p.com", ttl_seconds=10)
        assert rl.ttl_seconds == MIN_TTL_SECONDS

    def test_ttl_clamp_above_max(self):
        rl = RevocationList(issuer="https://p.com", ttl_seconds=9999)
        assert rl.ttl_seconds == MAX_TTL_SECONDS

    def test_ttl_within_range(self):
        rl = RevocationList(issuer="https://p.com", ttl_seconds=120)
        assert rl.ttl_seconds == 120

    def test_revoke_adds_entry(self):
        rl = RevocationList(issuer="https://p.com")
        entry = rl.revoke("token-1", reason=REASON_USER_REVOKED)
        assert len(rl.entries) == 1
        assert entry.jti == "token-1"
        assert entry.reason == REASON_USER_REVOKED
        assert entry.revoked_at > 0

    def test_revoke_with_explicit_timestamp(self):
        rl = RevocationList(issuer="https://p.com")
        entry = rl.revoke("token-1", reason=REASON_COMPROMISED, revoked_at=12345)
        assert entry.revoked_at == 12345

    def test_is_revoked_found(self):
        rl = RevocationList(issuer="https://p.com")
        rl.revoke("token-abc", reason=REASON_USER_REVOKED)
        result = rl.is_revoked("token-abc")
        assert result is not None
        assert result.jti == "token-abc"

    def test_is_revoked_not_found(self):
        rl = RevocationList(issuer="https://p.com")
        rl.revoke("token-abc", reason=REASON_USER_REVOKED)
        assert rl.is_revoked("token-xyz") is None

    def test_prune_removes_old_entries(self):
        rl = RevocationList(issuer="https://p.com")
        rl.revoke("old-token", reason=REASON_USER_REVOKED, revoked_at=100)
        rl.revoke("new-token", reason=REASON_USER_REVOKED, revoked_at=500)
        removed = rl.prune(max_token_exp=300)
        assert removed == 1
        assert len(rl.entries) == 1
        assert rl.entries[0].jti == "new-token"
        assert rl.is_revoked("old-token") is None

    def test_prune_removes_nothing_when_all_recent(self):
        rl = RevocationList(issuer="https://p.com")
        rl.revoke("t1", reason=REASON_USER_REVOKED, revoked_at=500)
        removed = rl.prune(max_token_exp=100)
        assert removed == 0
        assert len(rl.entries) == 1

    def test_serialization_round_trip(self):
        rl = RevocationList(issuer="https://p.com", ttl_seconds=120, published_at=9999)
        rl.revoke("t1", reason=REASON_USER_REVOKED, revoked_at=100)
        rl.revoke("t2", reason=REASON_COMPROMISED, revoked_at=200)

        data = rl.to_dict()
        assert data["version"] == 1
        assert data["issuer"] == "https://p.com"
        assert data["ttl_seconds"] == 120
        assert data["published_at"] == 9999
        assert len(data["entries"]) == 2

        rl2 = RevocationList.from_dict(data)
        assert rl2.issuer == rl.issuer
        assert rl2.ttl_seconds == rl.ttl_seconds
        assert rl2.published_at == rl.published_at
        assert len(rl2.entries) == 2
        assert rl2.is_revoked("t1") is not None
        assert rl2.is_revoked("t2") is not None

    def test_from_dict_with_empty_entries(self):
        data = {"version": 1, "issuer": "https://p.com", "published_at": 100, "ttl_seconds": 60, "entries": []}
        rl = RevocationList.from_dict(data)
        assert len(rl.entries) == 0


# --- Verifier integration tests ---


class TestVerifierRevocation:
    def test_revoked_token_rejected(self, issuer, verifier, user_hash):
        token_str = issuer.create_token(
            agent_session="sess-1",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=Scopes.ecommerce_read(),
            ttl_seconds=3600,
        )
        # Extract jti from token
        import json, base64
        payload = json.loads(base64.urlsafe_b64decode(token_str.split(".")[1] + "=="))
        jti = payload["jti"]

        rl = RevocationList(issuer="https://test-platform.com")
        rl.revoke(jti, reason=REASON_USER_REVOKED)
        verifier.set_revocation_list(rl)

        result = verifier.verify(token_str, expected_audience=AUDIENCE)
        assert not result.valid
        assert result.reason == "Token revoked"
        assert result.revocation_reason == REASON_USER_REVOKED

    def test_non_revoked_token_passes(self, issuer, verifier, user_hash):
        token_str = issuer.create_token(
            agent_session="sess-2",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=Scopes.ecommerce_read(),
            ttl_seconds=3600,
        )
        rl = RevocationList(issuer="https://test-platform.com")
        rl.revoke("some-other-jti", reason=REASON_USER_REVOKED)
        verifier.set_revocation_list(rl)

        result = verifier.verify(token_str, expected_audience=AUDIENCE)
        assert result.valid

    def test_no_revocation_list_skips_check(self, issuer, verifier, user_hash):
        token_str = issuer.create_token(
            agent_session="sess-3",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=Scopes.ecommerce_read(),
            ttl_seconds=3600,
        )
        # No revocation list set — should pass as before
        result = verifier.verify(token_str, expected_audience=AUDIENCE)
        assert result.valid

    def test_clear_revocation_list(self, issuer, verifier, user_hash):
        token_str = issuer.create_token(
            agent_session="sess-4",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=Scopes.ecommerce_read(),
            ttl_seconds=3600,
        )
        import json, base64
        payload = json.loads(base64.urlsafe_b64decode(token_str.split(".")[1] + "=="))
        jti = payload["jti"]

        rl = RevocationList(issuer="https://test-platform.com")
        rl.revoke(jti, reason=REASON_COMPROMISED)
        verifier.set_revocation_list(rl)

        # Should be rejected
        result = verifier.verify(token_str, expected_audience=AUDIENCE)
        assert not result.valid

        # Clear the list — need a new token since jti replay protection
        token_str2 = issuer.create_token(
            agent_session="sess-4b",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=Scopes.ecommerce_read(),
            ttl_seconds=3600,
        )
        verifier.set_revocation_list(None)
        result2 = verifier.verify(token_str2, expected_audience=AUDIENCE)
        assert result2.valid
