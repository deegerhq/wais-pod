## Context

The PoD protocol lets agent platforms issue short-lived, scoped tokens that websites verify. Currently, once a token is issued, it remains valid until its `exp` timestamp — there is no way for a website to learn that a token has been revoked by the platform.

The demo platform (`pod_platform/`) has a local revoke button that marks tokens in an in-memory dict, but:
- The core `pod/verifier.py` never checks revocation status
- There is no standard endpoint or format for publishing revoked tokens
- The spec mentions revocation in one line without defining a protocol

Existing verification flow in `pod/verifier.py` performs: parse → header check → signature → build token → iat check → expiration → replay (jti) → audience → user_verified → scopes. Revocation checking needs to fit into this pipeline.

## Goals / Non-Goals

**Goals:**
- Define a standard revocation list format and endpoint that platforms publish
- Add a `RevocationList` class to the core `pod/` library for managing revoked tokens
- Integrate optional revocation checking into `PoDVerifier.verify()`
- Keep the mechanism simple, cacheable, and compatible with existing token flow
- Maintain full backward compatibility — revocation checking is opt-in

**Non-Goals:**
- Real-time push-based revocation (WebSockets, webhooks)
- Distributed revocation across multiple platforms
- Replacing the existing jti-based replay protection
- Modifying the token format itself (no new claims)

## Decisions

### 1. Revocation List over Token Introspection Endpoint

**Choice:** Platform publishes a static JSON revocation list at `/.well-known/wais-revocation` rather than providing a per-token introspection endpoint.

**Alternatives considered:**
- Per-token introspection (RFC 7662 style): More precise but adds a synchronous network call per verification, creating a single point of failure
- CRL-style signed lists: More complex cryptographic infrastructure than needed at this stage

**Rationale:** A cacheable list scales better — websites fetch it periodically and check locally. No per-request latency. Works even if the platform is temporarily down (stale cache).

### 2. Revocation List Format

**Choice:** JSON document with metadata and an array of revoked entries:
```json
{
  "version": 1,
  "issuer": "https://agent-platform.com",
  "published_at": 1708617600,
  "ttl_seconds": 300,
  "entries": [
    {
      "jti": "token-uuid",
      "revoked_at": 1708617500,
      "reason": "user_revoked"
    }
  ]
}
```

**Rationale:** Simple, human-readable, easy to cache. The `ttl_seconds` field tells verifiers how long to cache before re-fetching. Entries only need to persist until the original token's `exp` would have passed.

### 3. Opt-in Integration in PoDVerifier

**Choice:** Add an optional `revocation_list` parameter to `PoDVerifier` and a `set_revocation_list()` method. The verifier checks the list if present but does not fetch it — fetching is the caller's responsibility.

**Alternatives considered:**
- Auto-fetching inside the verifier: Would add HTTP dependency to the core library and make verification non-deterministic
- Middleware-only approach: Would not standardize the check in the core library

**Rationale:** Keeps the core library dependency-free (no HTTP client needed). The demo store or any integration can fetch the list on a timer and pass it to the verifier. This follows the existing pattern where the verifier is a pure validation object.

### 4. Revocation Entry Cleanup

**Choice:** `RevocationList` automatically prunes entries for tokens whose `exp` has passed, since expired tokens are already rejected by the verifier.

**Rationale:** Keeps the list small without manual management. A token that has naturally expired doesn't need to stay on the revocation list.

## Risks / Trade-offs

- **[Cache staleness]** → A token revoked between list refreshes remains valid for up to `ttl_seconds`. Mitigation: Recommend short TTL (60-300 seconds) and short token lifetimes (5-10 minutes).
- **[List size]** → High-volume platforms could have large lists. Mitigation: Auto-prune expired entries; recommend short token lifetimes to keep the active window small.
- **[No fetching in core lib]** → Integrators must implement their own fetch+cache logic. Mitigation: Provide clear examples and helper utilities in the demo apps.
- **[Backward compatibility]** → Existing verifiers that don't use revocation lists continue to work unchanged. No breaking changes.

## File Changes

| File | Change |
|------|--------|
| `pod/revocation.py` (new) | `RevocationEntry`, `RevocationList` classes with serialization, lookup, and pruning |
| `pod/__init__.py` | Export `RevocationList`, `RevocationEntry` |
| `pod/verifier.py` | Add optional `revocation_list` param, `set_revocation_list()` method, and revocation check step between signature verification and expiration check |
| `spec/WAIS-Spec-Draft-v0.1.md` | Expand Section 5.6 with revocation list protocol details |
| `tests/test_revocation.py` (new) | Tests for RevocationList creation, serialization, lookup, pruning, and verifier integration |
| `tests/conftest.py` | Add revocation-related fixtures |
| `openspec/specs/token-revocation/spec.md` (new) | Formal spec for revocation protocol |
| `openspec/specs/pod-verification/spec.md` | Delta spec adding revocation check requirement |
