## Purpose

Define the structure and behavior of the Proof of Delegation (PoD) token — the JWT-like credential that agents present to websites to prove they have been delegated authority by a real human user.

## Requirements

### Requirement: Token structure follows JWT-like format
The PoD token SHALL consist of three parts: header, payload, and signature, encoded in base64url and separated by dots.

#### Scenario: Token has valid three-part structure
- **WHEN** a PoD token string is created
- **THEN** it SHALL contain exactly three dot-separated base64url-encoded segments (header.payload.signature)

### Requirement: Header contains algorithm and type
The token header SHALL include the signing algorithm (`alg`), token type (`typ`), and optionally a key identifier (`kid`).

#### Scenario: Header uses ES256 algorithm
- **WHEN** a token is created
- **THEN** the header `alg` field SHALL be "ES256"

#### Scenario: Header declares WAIS-PoD type
- **WHEN** a token is created
- **THEN** the header `typ` field SHALL be "WAIS-PoD"

### Requirement: Payload contains standard JWT claims
The token payload SHALL include `iss` (issuer platform URL), `sub` (agent session ID prefixed with "agent:"), `aud` (target website URL), `iat` (issued-at timestamp), `exp` (expiration timestamp), and optionally `jti` (unique token ID for replay protection).

#### Scenario: Agent session ID is prefixed
- **WHEN** a token is issued for agent session "session-abc123"
- **THEN** the `sub` claim SHALL be "agent:session-abc123"

#### Scenario: Token has expiration
- **WHEN** a token is created with a TTL of 3600 seconds
- **THEN** the `exp` claim SHALL equal `iat` + 3600

### Requirement: Payload contains delegation section
The token payload SHALL include a `delegation` object containing `user_hash`, `user_verified`, `consent_timestamp`, `scopes`, and `constraints`.

#### Scenario: User hash is privacy-preserving
- **WHEN** a user ID is hashed for delegation
- **THEN** the `user_hash` SHALL be in format "sha256:<hex-digest>" using SHA-256

#### Scenario: Scopes are listed in delegation
- **WHEN** a token is created with scopes ["catalog.browse", "cart.modify"]
- **THEN** the `delegation.scopes` array SHALL contain exactly those scopes

### Requirement: Constraints limit delegation authority
The constraints object SHALL support `max_transaction_amount`, `require_confirmation_above`, `allowed_domains`, and `geo_restrictions`.

#### Scenario: Transaction amount has currency
- **WHEN** a max transaction constraint is set
- **THEN** it SHALL include both `value` (numeric) and `currency` (string, e.g., "EUR")

#### Scenario: Amount exceeds limit
- **WHEN** an action amount exceeds `max_transaction_amount.value` in the same currency
- **THEN** the `exceeds_amount` check SHALL return true

#### Scenario: Confirmation threshold triggers
- **WHEN** an action amount exceeds `require_confirmation_above.value` in the same currency
- **THEN** the `needs_confirmation` check SHALL return true

#### Scenario: Currency mismatch requires confirmation
- **WHEN** the action currency differs from the constraint currency
- **THEN** both `exceeds_amount` and `needs_confirmation` SHALL return true

### Requirement: Token expiration is checkable
The token SHALL expose an `is_expired` property based on the current time and the `exp` claim.

#### Scenario: Expired token detected
- **WHEN** the current time is past the token's `exp` value
- **THEN** `is_expired` SHALL return true

### Requirement: Scopes support wildcard matching
The delegation SHALL support wildcard scope patterns using ".*" suffix to match any action within a namespace.

#### Scenario: Wildcard scope matches specific action
- **WHEN** a delegation has scope "catalog.*"
- **THEN** `has_scope("catalog.browse")` SHALL return true

#### Scenario: Wildcard does not match different namespace
- **WHEN** a delegation has scope "catalog.*"
- **THEN** `has_scope("cart.modify")` SHALL return false
