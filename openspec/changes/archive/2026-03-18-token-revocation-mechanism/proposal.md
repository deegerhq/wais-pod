## Why

The PoD protocol currently has no standard mechanism for websites (verifiers) to discover that a token has been revoked. While the demo platform allows users to revoke tokens locally, the verifier has no way to check revocation status — it will keep accepting a revoked token until it naturally expires (up to 1 hour). This creates a security gap: if a token is compromised or a user withdraws consent, there is no protocol-level way to enforce that revocation across verifying websites.

## What Changes

- Introduce a **standard revocation list endpoint** (`/.well-known/wais-revocation`) that agent platforms publish, containing recently revoked token JTIs
- Define a **revocation list format** with metadata (publish time, TTL, next update) and a list of revoked token entries
- Add **revocation checking to the verifier** so `PoDVerifier` can fetch, cache, and consult a revocation list during token verification
- Add a **`RevocationList` class** to the core library for platforms to manage and serialize their revoked tokens
- Recommend **shorter default token lifetimes** (5-10 minutes) to reduce the window of vulnerability
- Expand the revocation section in the main WAIS spec beyond the current one-line mention

## Non-goals

- Real-time push-based revocation (e.g., WebSocket notifications) — too complex for v1
- Distributed revocation consensus across multiple platforms
- Replacing the existing replay protection mechanism in the verifier

## Capabilities

### New Capabilities
- `token-revocation`: Standard protocol for publishing and consuming token revocation lists, including endpoint format, list structure, caching behavior, and verifier integration

### Modified Capabilities
- `pod-verification`: Add revocation list checking as an optional verification step during token validation

## Impact

- **pod/verifier.py**: Add optional revocation list fetching and checking during `verify()`
- **pod/ (new file)**: New `revocation.py` module with `RevocationList` and `RevocationEntry` classes
- **pod/__init__.py**: Export new revocation classes
- **spec/WAIS-Spec-Draft-v0.1.md**: Expand Section 5.6 (Revocation) with protocol details
- **tests/**: New `test_revocation.py` for revocation list creation, serialization, and verifier integration
- **Dependencies**: May need `httpx` or similar for async HTTP fetching of revocation lists (or use stdlib `urllib`)
