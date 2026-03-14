"""Tests for token/scope reuse behavior during delegation period.

Verifies that:
- A single token (same jti) CANNOT be reused (replay protection).
- Multiple tokens with the SAME scopes CAN be issued and used independently.
- Different actions under the same scope work with fresh tokens.
- Scope reuse works across different audiences with fresh tokens.
"""

from pod.issuer import PoDIssuer
from pod.verifier import PoDVerifier
from pod.scopes import Scopes

from tests.conftest import PLATFORM_URL, AUDIENCE


class TestScopeReuseSameVerifier:
    """Multiple tokens with the same scopes against one verifier."""

    def test_same_scope_multiple_tokens_all_accepted(self, issuer, verifier, user_hash):
        """Fresh tokens with identical scopes should all verify successfully."""
        scopes = [Scopes.CATALOG_BROWSE, Scopes.CART_MODIFY]

        results = []
        for i in range(5):
            token = issuer.create_token(
                agent_session=f"session-{i}",
                audience=AUDIENCE,
                user_hash=user_hash,
                scopes=scopes,
                ttl_seconds=3600,
            )
            result = verifier.verify(
                token,
                required_scopes=[Scopes.CATALOG_BROWSE],
                expected_audience=AUDIENCE,
            )
            results.append(result)

        assert all(r.valid for r in results), (
            f"All tokens should be valid; failures: "
            f"{[(i, r.reason) for i, r in enumerate(results) if not r.valid]}"
        )

    def test_same_session_multiple_tokens_all_accepted(self, issuer, verifier, user_hash):
        """Even with the same session id, fresh tokens (new jti) pass."""
        scopes = [Scopes.CATALOG_BROWSE]

        results = []
        for _ in range(3):
            token = issuer.create_token(
                agent_session="same-session",
                audience=AUDIENCE,
                user_hash=user_hash,
                scopes=scopes,
                ttl_seconds=3600,
            )
            result = verifier.verify(
                token,
                required_scopes=[Scopes.CATALOG_BROWSE],
                expected_audience=AUDIENCE,
            )
            results.append(result)

        assert all(r.valid for r in results)

    def test_replay_same_token_rejected(self, issuer, verifier, user_hash):
        """Presenting the exact same token string twice is rejected."""
        token = issuer.create_token(
            agent_session="session-replay",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=[Scopes.CATALOG_BROWSE],
            ttl_seconds=3600,
        )

        first = verifier.verify(token, expected_audience=AUDIENCE)
        assert first.valid is True

        second = verifier.verify(token, expected_audience=AUDIENCE)
        assert second.valid is False
        assert "replay" in second.reason.lower()

    def test_different_scopes_across_tokens(self, issuer, verifier, user_hash):
        """Token A uses catalog.browse, Token B uses cart.modify — both accepted."""
        token_a = issuer.create_token(
            agent_session="session-a",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=[Scopes.CATALOG_BROWSE],
            ttl_seconds=3600,
        )
        token_b = issuer.create_token(
            agent_session="session-b",
            audience=AUDIENCE,
            user_hash=user_hash,
            scopes=[Scopes.CART_MODIFY],
            ttl_seconds=3600,
        )

        result_a = verifier.verify(
            token_a,
            required_scopes=[Scopes.CATALOG_BROWSE],
            expected_audience=AUDIENCE,
        )
        result_b = verifier.verify(
            token_b,
            required_scopes=[Scopes.CART_MODIFY],
            expected_audience=AUDIENCE,
        )

        assert result_a.valid is True
        assert result_b.valid is True


class TestScopeReuseAcrossAudiences:
    """Scope reuse when targeting different sites."""

    def test_same_scopes_different_audiences(self, keypair, user_hash):
        """Same user/scopes can create tokens for different sites."""
        priv, pub = keypair
        issuer = PoDIssuer(platform_url=PLATFORM_URL, private_key_pem=priv)

        store_a = "https://store-a.com"
        store_b = "https://store-b.com"

        token_a = issuer.create_token(
            agent_session="session-1",
            audience=store_a,
            user_hash=user_hash,
            scopes=[Scopes.CATALOG_BROWSE, Scopes.CHECKOUT_EXECUTE],
            ttl_seconds=3600,
        )
        token_b = issuer.create_token(
            agent_session="session-2",
            audience=store_b,
            user_hash=user_hash,
            scopes=[Scopes.CATALOG_BROWSE, Scopes.CHECKOUT_EXECUTE],
            ttl_seconds=3600,
        )

        verifier_a = PoDVerifier()
        verifier_a.add_trusted_platform_pem(PLATFORM_URL, pub)

        verifier_b = PoDVerifier()
        verifier_b.add_trusted_platform_pem(PLATFORM_URL, pub)

        result_a = verifier_a.verify(
            token_a,
            required_scopes=[Scopes.CHECKOUT_EXECUTE],
            expected_audience=store_a,
        )
        result_b = verifier_b.verify(
            token_b,
            required_scopes=[Scopes.CHECKOUT_EXECUTE],
            expected_audience=store_b,
        )

        assert result_a.valid is True
        assert result_b.valid is True


class TestScopeReuseDuringDuration:
    """Verify scope reuse throughout token TTL with constraints."""

    def test_high_risk_scope_reusable_with_fresh_tokens(self, issuer, verifier, user_hash):
        """High-risk scopes (checkout.execute) can be reused via fresh tokens."""
        for i in range(3):
            token = issuer.create_token(
                agent_session=f"checkout-{i}",
                audience=AUDIENCE,
                user_hash=user_hash,
                scopes=[Scopes.CHECKOUT_EXECUTE],
                constraints={
                    "max_transaction_amount": {"value": 500, "currency": "EUR"},
                    "require_confirmation_above": {"value": 100, "currency": "EUR"},
                },
                ttl_seconds=3600,
            )
            result = verifier.verify(
                token,
                required_scopes=[Scopes.CHECKOUT_EXECUTE],
                expected_audience=AUDIENCE,
            )
            assert result.valid is True, f"Token {i} failed: {result.reason}"
            # Constraint checks still apply per-token
            assert result.requires_confirmation(250, "EUR") is True
            assert result.requires_confirmation(50, "EUR") is False
            assert result.exceeds_limit(600, "EUR") is True
            assert result.exceeds_limit(400, "EUR") is False

