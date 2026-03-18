## Purpose

Define the confirmation challenge-response protocol used when agents attempt high-risk actions that require explicit user approval before proceeding.

## Requirements

### Requirement: Sites can create confirmation challenges
The system SHALL provide a `ConfirmationChallenge` that sites send to agents when an action exceeds the risk threshold.

#### Scenario: Challenge creation with defaults
- **WHEN** a challenge is created with `action="checkout"` and `risk_level="high"`
- **THEN** it SHALL have a unique `challenge_id` prefixed with "conf_", a TTL of 300 seconds, and default approval method "user_confirm"

#### Scenario: Challenge has expiration
- **WHEN** a challenge is created with `ttl_seconds=300`
- **THEN** `expires_at` SHALL be set to current time + 300

### Requirement: Challenges include display information for users
The challenge SHALL include a `display_to_user` dict that the agent platform presents to the user for approval.

#### Scenario: Challenge includes action details
- **WHEN** a checkout challenge is created with display info including summary, total, and items
- **THEN** `display_to_user` SHALL contain all provided details for the user to review

### Requirement: Challenges define approval methods
The challenge SHALL specify which `approval_methods` are acceptable (e.g., "user_confirm", "biometric").

#### Scenario: Multiple approval methods
- **WHEN** a critical-risk challenge is created with methods ["user_confirm", "biometric"]
- **THEN** the agent platform MAY use any of the listed methods

### Requirement: Challenge expiration is checkable
The challenge SHALL expose an `is_expired` property.

#### Scenario: Expired challenge detected
- **WHEN** the current time exceeds the challenge's `expires_at`
- **THEN** `is_expired` SHALL return true

### Requirement: Challenge serializes to standard format
The challenge SHALL serialize to a dict with a `wais_confirmation` wrapper key containing all challenge fields.

#### Scenario: Serialization format
- **WHEN** `to_dict()` is called on a challenge
- **THEN** the result SHALL have the structure `{"wais_confirmation": {"challenge_id": ..., "action": ..., "risk_level": ..., "expires_at": ..., "display_to_user": ..., "approval_methods": ...}}`

### Requirement: Agents return confirmation responses
The system SHALL provide a `ConfirmationResponse` that agent platforms send back after obtaining user approval.

#### Scenario: Valid confirmation response
- **WHEN** a response has `challenge_id`, `approved=true`, `user_hash`, and `platform_signature`
- **THEN** `is_valid` SHALL return true

#### Scenario: Invalid confirmation response
- **WHEN** a response is missing `user_hash` or `platform_signature`
- **THEN** `is_valid` SHALL return false

### Requirement: Confirmation response serializes to standard format
The response SHALL serialize to a dict with a `wais_confirmation_response` wrapper key.

#### Scenario: Response serialization
- **WHEN** `to_dict()` is called on a response
- **THEN** the result SHALL have the structure `{"wais_confirmation_response": {"challenge_id": ..., "approved": ..., "approval_method": ..., "approved_at": ..., "user_hash": ..., "platform_signature": ...}}`

### Requirement: Risk levels determine confirmation behavior
The system SHALL follow these confirmation rules: low = no confirmation, medium = soft confirmation, high = hard confirmation required, critical = strong authentication (biometric/2FA).

#### Scenario: High risk requires hard confirmation
- **WHEN** an action has risk level "high"
- **THEN** the site SHALL generate a confirmation challenge that the user MUST approve before the action proceeds

#### Scenario: Low risk skips confirmation
- **WHEN** an action has risk level "low"
- **THEN** the agent MAY proceed without any confirmation
