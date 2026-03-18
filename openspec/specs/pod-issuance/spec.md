## Purpose

Define how agent platforms issue signed PoD tokens — generating key pairs, creating tokens with delegation payloads, and signing them using ES256.

## Requirements

### Requirement: Issuer creates signed PoD tokens
The issuer SHALL create cryptographically signed PoD tokens using ES256 (ECDSA P-256 with SHA-256) that can be verified by any party with the corresponding public key.

#### Scenario: Token is signed and verifiable
- **WHEN** a token is created with valid parameters
- **THEN** the resulting token string SHALL be verifiable using the issuer's public key

### Requirement: Issuer accepts private key from file or PEM bytes
The issuer SHALL support initialization with either a file path to a PEM-encoded private key or raw PEM bytes.

#### Scenario: Initialize with key file
- **WHEN** `private_key_path` is provided
- **THEN** the issuer SHALL load and use that key for signing

#### Scenario: Initialize with PEM bytes
- **WHEN** `private_key_pem` bytes are provided
- **THEN** the issuer SHALL load and use that key for signing

#### Scenario: No key provided
- **WHEN** neither `private_key_path` nor `private_key_pem` is provided
- **THEN** initialization SHALL raise a ValueError

### Requirement: Issuer can generate ES256 key pairs
The issuer SHALL provide a static method to generate new ECDSA P-256 key pairs suitable for PoD token signing.

#### Scenario: Key pair generation
- **WHEN** `generate_keypair()` is called
- **THEN** it SHALL return a tuple of (private_key_pem, public_key_pem) in PEM format

### Requirement: Issuer creates tokens with all required fields
The `create_token` method SHALL produce tokens with all required JWT claims (`iss`, `sub`, `aud`, `iat`, `exp`, `jti`) and the delegation payload (`user_hash`, `user_verified`, `consent_timestamp`, `scopes`, `constraints`).

#### Scenario: Token has unique JTI
- **WHEN** a token is created
- **THEN** the `jti` claim SHALL be a unique UUID

#### Scenario: Token subject is prefixed
- **WHEN** a token is created for agent session "session-123"
- **THEN** the `sub` claim SHALL be "agent:session-123"

#### Scenario: Token TTL is configurable
- **WHEN** a token is created with `ttl_seconds=1800`
- **THEN** `exp` SHALL equal `iat` + 1800

### Requirement: Issuer uses RFC 7518 signature format
The issuer SHALL encode ES256 signatures in R||S format (64 bytes, big-endian) per RFC 7518 for JWS compatibility.

#### Scenario: Signature is R||S format
- **WHEN** a token is signed
- **THEN** the signature segment SHALL be 64 bytes of raw R||S (base64url-encoded)
