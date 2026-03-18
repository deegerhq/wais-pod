## Purpose

Define how websites verify PoD tokens presented by agents — validating signatures, checking expiration, enforcing scopes, and providing replay protection.

## Requirements

### Requirement: Verifier validates token signature
The verifier SHALL validate the cryptographic signature of a PoD token against the issuing platform's public key using ES256 (ECDSA P-256 with SHA-256).

#### Scenario: Valid signature passes
- **WHEN** a token is signed by a trusted platform's private key
- **THEN** signature verification SHALL succeed

#### Scenario: Tampered token fails
- **WHEN** a token's payload has been modified after signing
- **THEN** signature verification SHALL fail with reason "Invalid signature"

### Requirement: Verifier supports both signature formats
The verifier SHALL accept ES256 signatures in both R||S format (RFC 7518, 64 bytes) and DER format for backward compatibility.

#### Scenario: R||S format signature
- **WHEN** a 64-byte raw signature is presented
- **THEN** the verifier SHALL convert R||S to DER before cryptographic verification

#### Scenario: DER format signature
- **WHEN** a non-64-byte signature is presented
- **THEN** the verifier SHALL treat it as DER format directly

### Requirement: Verifier checks token type
The verifier SHALL reject tokens that do not have `typ: "WAIS-PoD"` in the header.

#### Scenario: Wrong token type rejected
- **WHEN** a token has `typ: "JWT"` instead of "WAIS-PoD"
- **THEN** verification SHALL fail with reason "Invalid token type"

### Requirement: Verifier checks algorithm
The verifier SHALL only accept tokens with `alg: "ES256"` in the header.

#### Scenario: Unsupported algorithm rejected
- **WHEN** a token has `alg: "RS256"`
- **THEN** verification SHALL fail with reason indicating unsupported algorithm

### Requirement: Verifier checks platform trust
The verifier SHALL only accept tokens from platforms whose public keys have been registered via `add_trusted_platform` or `add_trusted_platform_pem`.

#### Scenario: Unknown platform rejected
- **WHEN** a token's `iss` does not match any trusted platform
- **THEN** verification SHALL fail with reason "Unknown platform: <issuer>"

### Requirement: Verifier checks token expiration
The verifier SHALL reject tokens whose `exp` timestamp is in the past, with a configurable clock skew tolerance (default 30 seconds).

#### Scenario: Expired token rejected
- **WHEN** a token's `exp` is more than clock_skew_seconds in the past
- **THEN** verification SHALL fail with reason "Token expired"

#### Scenario: Future-issued token rejected
- **WHEN** a token's `iat` is more than clock_skew_seconds in the future
- **THEN** verification SHALL fail with reason "Token issued in the future"

### Requirement: Verifier checks audience
The verifier SHALL optionally validate that the token's `aud` claim matches the expected audience (the verifying site's URL).

#### Scenario: Audience mismatch rejected
- **WHEN** `expected_audience` is provided and does not match token's `aud`
- **THEN** verification SHALL fail with reason "Audience mismatch"

### Requirement: Verifier checks user verification status
The verifier SHALL reject tokens where `delegation.user_verified` is false.

#### Scenario: Unverified user rejected
- **WHEN** a token has `user_verified: false`
- **THEN** verification SHALL fail with reason "User not verified"

### Requirement: Verifier checks required scopes
The verifier SHALL optionally validate that the token's delegation includes all required scopes for the requested action.

#### Scenario: Missing scope rejected
- **WHEN** `required_scopes` includes "checkout.execute" but the token only has "catalog.browse"
- **THEN** verification SHALL fail with reason listing the missing scopes

### Requirement: Verifier provides replay protection
The verifier SHALL track seen `jti` values and reject tokens with duplicate JTIs. Additionally, the verifier SHALL optionally check a provided revocation list and reject tokens whose `jti` appears in the list.

#### Scenario: Replayed token rejected
- **WHEN** a token with the same `jti` is presented a second time
- **THEN** verification SHALL fail with reason "Token already used (replay)"

#### Scenario: Revoked token rejected
- **WHEN** a revocation list is configured on the verifier and a token's `jti` appears in the revocation list
- **THEN** verification SHALL fail with reason "Token revoked" and the result SHALL include the revocation reason

#### Scenario: Token passes when not in revocation list
- **WHEN** a revocation list is configured but the token's `jti` is not in the list
- **THEN** the revocation check SHALL pass and verification SHALL continue to the next step

#### Scenario: No revocation list configured
- **WHEN** no revocation list has been set on the verifier
- **THEN** the revocation check SHALL be skipped and verification SHALL continue as before (backward compatible)

### Requirement: Verifier accepts revocation list configuration
The verifier SHALL provide a `set_revocation_list()` method that accepts a `RevocationList` object. The verifier SHALL use this list during token verification when present.

#### Scenario: Set revocation list
- **WHEN** `set_revocation_list(revocation_list)` is called with a valid RevocationList
- **THEN** the verifier SHALL use this list for subsequent `verify()` calls

#### Scenario: Update revocation list
- **WHEN** `set_revocation_list()` is called with a new RevocationList replacing an existing one
- **THEN** the verifier SHALL use the new list for subsequent verifications

#### Scenario: Clear revocation list
- **WHEN** `set_revocation_list(None)` is called
- **THEN** the verifier SHALL stop checking revocation and behave as if no list was configured

### Requirement: Verification result includes confirmation check
The verification result SHALL provide `requires_confirmation` and `exceeds_limit` methods that check the token's constraints against an action amount.

#### Scenario: Action above confirmation threshold
- **WHEN** a valid token has `require_confirmation_above` of 100 EUR and the action is 150 EUR
- **THEN** `requires_confirmation(150, "EUR")` SHALL return true
