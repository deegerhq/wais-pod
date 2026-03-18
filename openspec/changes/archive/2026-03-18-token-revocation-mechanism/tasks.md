## 1. Core Revocation Library

- [x] 1.1 Create `pod/revocation.py` with `RevocationEntry` dataclass (jti, revoked_at, reason fields) and valid reason constants
- [x] 1.2 Add `RevocationList` class with constructor (issuer, ttl_seconds with 60-300 clamping, entries list)
- [x] 1.3 Add `revoke()` method to RevocationList for adding entries by jti and reason
- [x] 1.4 Add `is_revoked()` method to RevocationList for looking up a jti, returning entry or None
- [x] 1.5 Add `prune()` method to RevocationList for removing entries for expired tokens
- [x] 1.6 Add `to_dict()` and `from_dict()` serialization methods to RevocationList
- [x] 1.7 Export `RevocationList` and `RevocationEntry` from `pod/__init__.py`

## 2. Verifier Integration

- [x] 2.1 Add `_revocation_list` attribute and `set_revocation_list()` method to `PoDVerifier`
- [x] 2.2 Add revocation check step in `PoDVerifier.verify()` between replay protection and audience check — reject with reason "Token revoked" if jti is in the revocation list
- [x] 2.3 Include revocation reason in the `VerificationResult` when a token is rejected as revoked

## 3. Tests

- [x] 3.1 Create `tests/test_revocation.py` with tests for RevocationEntry creation and reason validation
- [x] 3.2 Add tests for RevocationList creation, ttl_seconds clamping, and serialization round-trip
- [x] 3.3 Add tests for `revoke()`, `is_revoked()`, and `prune()` methods
- [x] 3.4 Add tests for verifier integration: revoked token rejected, non-revoked token passes, no list configured skips check
- [x] 3.5 Add revocation-related fixtures to `tests/conftest.py`

## 4. Specification Updates

- [x] 4.1 Create `openspec/specs/token-revocation/spec.md` from the change spec (copy to canonical location)
- [x] 4.2 Update `openspec/specs/pod-verification/spec.md` with the revocation check requirement
- [x] 4.3 Expand Section 5.6 (Revocation) in `spec/WAIS-Spec-Draft-v0.1.md` with revocation list protocol details, endpoint format, and TTL guidance

## 5. Documentation

- [x] 5.1 Update `README.md` with revocation list section covering usage of RevocationList and verifier integration
