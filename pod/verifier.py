"""
PoD Token Verifier.

Used by websites to verify that an agent has valid
delegation from a real human user.
"""

from __future__ import annotations

import json
import time
import base64
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

from pod.token import PoDToken, DelegationPayload, Constraints
from pod.revocation import RevocationList


@dataclass
class VerificationResult:
    """Result of a PoD token verification."""

    valid: bool
    token: Optional[PoDToken] = None
    reason: Optional[str] = None
    revocation_reason: Optional[str] = None

    def requires_confirmation(self, action_amount: float = 0, currency: str = "EUR") -> bool:
        """Check if the action requires user confirmation."""
        if not self.valid or not self.token:
            return True
        return self.token.delegation.constraints.needs_confirmation(action_amount, currency)

    def exceeds_limit(self, action_amount: float = 0, currency: str = "EUR") -> bool:
        """Check if the action exceeds the maximum authorized amount."""
        if not self.valid or not self.token:
            return True
        return self.token.delegation.constraints.exceeds_amount(action_amount, currency)


class PoDVerifier:
    """Verifies Proof of Delegation tokens presented by agents."""

    def __init__(
        self,
        trusted_platforms: Optional[dict[str, str]] = None,
        registry_url: Optional[str] = None,
        allow_expired: bool = False,
        clock_skew_seconds: int = 30,
    ):
        """
        Args:
            trusted_platforms: Dict mapping platform URL -> path to public key PEM file.
            registry_url: URL of a PoD platform registry for dynamic key discovery.
            allow_expired: If True, don't reject expired tokens (for testing only).
            clock_skew_seconds: Allowed clock drift in seconds.
        """
        self._platform_keys: dict[str, ec.EllipticCurvePublicKey] = {}
        self._registry_url = registry_url
        self._allow_expired = allow_expired
        self._clock_skew_seconds = clock_skew_seconds
        self._seen_jtis: set[str] = set()
        self._revocation_list: Optional[RevocationList] = None

        if trusted_platforms:
            for platform_url, key_path in trusted_platforms.items():
                self.add_trusted_platform(platform_url, key_path)

    def add_trusted_platform(self, platform_url: str, public_key_path: str) -> None:
        """Add a trusted agent platform with its public key."""
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise ValueError(f"Expected EC public key for {platform_url}")
        self._platform_keys[platform_url] = public_key

    def add_trusted_platform_pem(self, platform_url: str, public_key_pem: bytes) -> None:
        """Add a trusted agent platform with its public key PEM bytes."""
        public_key = serialization.load_pem_public_key(public_key_pem)
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise ValueError(f"Expected EC public key for {platform_url}")
        self._platform_keys[platform_url] = public_key

    def set_revocation_list(self, revocation_list: Optional[RevocationList]) -> None:
        """Set or clear the revocation list used during verification."""
        self._revocation_list = revocation_list

    def verify(
        self,
        token_string: str,
        required_scopes: Optional[list[str]] = None,
        expected_audience: Optional[str] = None,
    ) -> VerificationResult:
        """Verify a PoD token.

        Args:
            token_string: The encoded PoD token from the request header.
            required_scopes: Scopes required for the requested action.
            expected_audience: The expected audience (your site URL).

        Returns:
            VerificationResult with validation status and parsed token.
        """
        # 1. Parse the token
        try:
            parts = token_string.split(".")
            if len(parts) != 3:
                return VerificationResult(valid=False, reason="Invalid token format")

            header = json.loads(self._b64url_decode(parts[0]))
            payload = json.loads(self._b64url_decode(parts[1]))
            raw_signature = self._b64url_decode_bytes(parts[2])
        except Exception as e:
            return VerificationResult(valid=False, reason=f"Token parsing failed: {e}")

        # 2. Validate header
        if header.get("typ") != "WAIS-PoD":
            return VerificationResult(valid=False, reason="Invalid token type")
        if header.get("alg") != "ES256":
            return VerificationResult(valid=False, reason=f"Unsupported algorithm: {header.get('alg')}")

        # 3. Check issuer is trusted
        issuer = payload.get("iss", "")
        if issuer not in self._platform_keys:
            return VerificationResult(valid=False, reason=f"Unknown platform: {issuer}")

        # 4. Verify signature (convert R||S back to DER)
        public_key = self._platform_keys[issuer]
        signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
        try:
            if len(raw_signature) == 64:
                # R||S format (RFC 7518) — convert to DER for cryptography lib
                r = int.from_bytes(raw_signature[:32], byteorder="big")
                s = int.from_bytes(raw_signature[32:], byteorder="big")
                der_signature = utils.encode_dss_signature(r, s)
            else:
                # Legacy DER format for backward compatibility
                der_signature = raw_signature
            public_key.verify(der_signature, signing_input, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature:
            return VerificationResult(valid=False, reason="Invalid signature")

        # 5. Build token object
        delegation_data = payload.get("delegation", {})
        constraints_data = delegation_data.get("constraints", {})

        token = PoDToken(
            alg=header.get("alg", "ES256"),
            typ=header.get("typ", "WAIS-PoD"),
            kid=header.get("kid"),
            iss=issuer,
            sub=payload.get("sub", ""),
            aud=payload.get("aud", ""),
            iat=payload.get("iat", 0),
            exp=payload.get("exp", 0),
            jti=payload.get("jti"),
            delegation=DelegationPayload(
                user_hash=delegation_data.get("user_hash", ""),
                user_verified=delegation_data.get("user_verified", False),
                consent_timestamp=delegation_data.get("consent_timestamp", 0),
                scopes=delegation_data.get("scopes", []),
                constraints=Constraints(
                    max_transaction_amount=constraints_data.get("max_transaction_amount"),
                    require_confirmation_above=constraints_data.get("require_confirmation_above"),
                    allowed_domains=constraints_data.get("allowed_domains"),
                    geo_restrictions=constraints_data.get("geo_restrictions"),
                ),
            ),
        )

        # 6. Check iat not in the future
        now = time.time()
        if not self._allow_expired and token.iat > now + self._clock_skew_seconds:
            return VerificationResult(valid=False, token=token, reason="Token issued in the future")

        # 7. Check expiration (with clock skew tolerance)
        if not self._allow_expired and now > token.exp + self._clock_skew_seconds:
            return VerificationResult(valid=False, token=token, reason="Token expired")

        # 8. Replay protection via jti
        if token.jti:
            if token.jti in self._seen_jtis:
                return VerificationResult(valid=False, token=token, reason="Token already used (replay)")
            self._seen_jtis.add(token.jti)

        # 8b. Revocation check (opt-in)
        if self._revocation_list and token.jti:
            entry = self._revocation_list.is_revoked(token.jti)
            if entry:
                return VerificationResult(
                    valid=False,
                    token=token,
                    reason="Token revoked",
                    revocation_reason=entry.reason,
                )

        # 9. Check audience
        if expected_audience and token.aud != expected_audience:
            return VerificationResult(valid=False, token=token, reason="Audience mismatch")

        # 10. Check user verification
        if not token.delegation.user_verified:
            return VerificationResult(valid=False, token=token, reason="User not verified")

        # 11. Check required scopes
        if required_scopes and not token.delegation.has_all_scopes(required_scopes):
            missing = [s for s in required_scopes if not token.delegation.has_scope(s)]
            return VerificationResult(
                valid=False, token=token, reason=f"Missing scopes: {missing}"
            )

        return VerificationResult(valid=True, token=token)

    @staticmethod
    def _b64url_decode(data: str) -> str:
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data).decode("utf-8")

    @staticmethod
    def _b64url_decode_bytes(data: str) -> bytes:
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)
