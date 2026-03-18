## MODIFIED Requirements

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

## ADDED Requirements

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
