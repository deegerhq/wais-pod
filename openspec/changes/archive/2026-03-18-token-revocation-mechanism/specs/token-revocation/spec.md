## ADDED Requirements

### Requirement: Platform publishes revocation list at well-known endpoint
The agent platform SHALL publish a JSON revocation list at `/.well-known/wais-revocation` containing all currently revoked tokens that have not yet expired.

#### Scenario: Revocation list is available
- **WHEN** a website fetches `https://<platform-url>/.well-known/wais-revocation`
- **THEN** the platform SHALL respond with a JSON document containing version, issuer, published_at, ttl_seconds, and entries fields

#### Scenario: Empty revocation list
- **WHEN** no tokens have been revoked
- **THEN** the platform SHALL respond with a valid revocation list where entries is an empty array

### Requirement: Revocation list follows standard format
The revocation list SHALL be a JSON document with the following structure: `version` (integer, currently 1), `issuer` (string, platform URL), `published_at` (integer, Unix timestamp), `ttl_seconds` (integer, cache duration), and `entries` (array of revocation entries).

#### Scenario: Valid revocation list structure
- **WHEN** a revocation list is serialized
- **THEN** it SHALL contain all required fields: version, issuer, published_at, ttl_seconds, and entries

#### Scenario: Version field
- **WHEN** a revocation list is created
- **THEN** the version field SHALL be set to 1

### Requirement: Revocation entry contains token identifier and metadata
Each entry in the revocation list SHALL contain `jti` (string, the token's unique identifier), `revoked_at` (integer, Unix timestamp when revocation occurred), and `reason` (string, one of: "user_revoked", "platform_revoked", "compromised", "superseded").

#### Scenario: Entry with user revocation
- **WHEN** a user revokes a token through the platform
- **THEN** the entry SHALL have reason "user_revoked" and the jti matching the revoked token

#### Scenario: Entry with compromise reason
- **WHEN** a platform detects a token may be compromised
- **THEN** the entry SHALL have reason "compromised"

### Requirement: Revocation list supports cache control via TTL
The `ttl_seconds` field SHALL indicate how long a website may cache the revocation list before re-fetching. Platforms SHALL set `ttl_seconds` between 60 and 300 seconds.

#### Scenario: TTL within valid range
- **WHEN** a revocation list is created with ttl_seconds of 120
- **THEN** the list SHALL be valid and websites MAY cache it for 120 seconds

#### Scenario: TTL below minimum
- **WHEN** a revocation list is created with ttl_seconds below 60
- **THEN** the RevocationList SHALL reject the value or clamp to 60

### Requirement: RevocationList provides token lookup
The `RevocationList` class SHALL provide a method to check whether a given `jti` appears in the revocation list, returning the revocation entry if found or None if not revoked.

#### Scenario: Revoked token found
- **WHEN** `is_revoked("token-abc")` is called and "token-abc" is in the entries
- **THEN** the method SHALL return the matching RevocationEntry

#### Scenario: Non-revoked token not found
- **WHEN** `is_revoked("token-xyz")` is called and "token-xyz" is not in the entries
- **THEN** the method SHALL return None

### Requirement: RevocationList supports adding and removing entries
The `RevocationList` class SHALL provide methods to add a revocation entry (by jti, reason, and optional revoked_at timestamp) and to prune entries for tokens that have expired.

#### Scenario: Add revocation entry
- **WHEN** `revoke("token-abc", reason="user_revoked")` is called
- **THEN** a new entry SHALL be added with the given jti, reason, and current timestamp as revoked_at

#### Scenario: Prune expired entries
- **WHEN** `prune(max_token_exp=<timestamp>)` is called
- **THEN** entries whose associated tokens have expired before the given timestamp SHALL be removed from the list

### Requirement: RevocationList supports serialization and deserialization
The `RevocationList` class SHALL provide `to_dict()` and `from_dict()` methods for JSON serialization and deserialization.

#### Scenario: Round-trip serialization
- **WHEN** a RevocationList is serialized with `to_dict()` and deserialized with `from_dict()`
- **THEN** the resulting list SHALL be equivalent to the original

#### Scenario: Deserialization from JSON
- **WHEN** a JSON document fetched from `/.well-known/wais-revocation` is passed to `from_dict()`
- **THEN** a valid RevocationList object SHALL be returned with all entries intact
