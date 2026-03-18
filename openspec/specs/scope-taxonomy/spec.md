## Purpose

Define the standard taxonomy of scopes organized by industry vertical, including naming conventions, risk level assignments, and convenience methods for common scope groupings.

## Requirements

### Requirement: Scopes follow namespace.action naming convention
All standard scopes SHALL follow the format `namespace.action` where namespace identifies the domain area and action identifies the operation.

#### Scenario: Valid scope format
- **WHEN** a scope is defined
- **THEN** it SHALL match the pattern `<namespace>.<action>` (e.g., "catalog.browse", "booking.create")

### Requirement: Every scope has a risk level
Every standard scope SHALL have an assigned risk level of "low", "medium", "high", or "critical".

#### Scenario: Risk level lookup
- **WHEN** `risk_level("catalog.browse")` is called
- **THEN** it SHALL return "low"

#### Scenario: Unknown scope defaults to medium
- **WHEN** `risk_level("custom.scope")` is called for an unregistered scope
- **THEN** it SHALL return "medium"

### Requirement: High-risk detection
The system SHALL provide an `is_high_risk` method that returns true for scopes with risk level "high" or "critical".

#### Scenario: High risk scope detected
- **WHEN** `is_high_risk("checkout.execute")` is called
- **THEN** it SHALL return true

#### Scenario: Low risk scope not flagged
- **WHEN** `is_high_risk("catalog.browse")` is called
- **THEN** it SHALL return false

### Requirement: E-Commerce vertical scopes
The system SHALL define scopes for e-commerce interactions: `catalog.browse` (low), `catalog.compare` (low), `cart.modify` (medium), `checkout.execute` (high), `order.track` (low), `return.initiate` (medium), `return.complete` (high), `subscription.manage` (high).

#### Scenario: E-Commerce read-only convenience
- **WHEN** `ecommerce_read()` is called
- **THEN** it SHALL return ["catalog.browse", "catalog.compare", "order.track"]

#### Scenario: E-Commerce full convenience
- **WHEN** `ecommerce_full()` is called
- **THEN** it SHALL return all e-commerce scopes including transactional ones

### Requirement: Travel and Hospitality vertical scopes
The system SHALL define scopes for travel: `availability.search` (low), `booking.create` (high), `booking.modify` (high), `booking.cancel` (high), `claim.submit` (medium).

#### Scenario: Travel full convenience
- **WHEN** `travel_full()` is called
- **THEN** it SHALL return all travel scopes

### Requirement: Financial Services vertical scopes
The system SHALL define scopes for financial services: `account.read` (medium), `quote.request` (low), `payment.execute` (critical), `dispute.file` (medium), `policy.modify` (high).

#### Scenario: Payment is critical risk
- **WHEN** `risk_level("payment.execute")` is called
- **THEN** it SHALL return "critical"

### Requirement: Government and Public Services vertical scopes
The system SHALL define scopes for government services: `appointment.book` (medium), `form.submit` (high), `document.request` (high), `status.check` (low).

#### Scenario: Form submission is high risk
- **WHEN** `risk_level("form.submit")` is called
- **THEN** it SHALL return "high"

### Requirement: Healthcare vertical scopes
The system SHALL define scopes for healthcare: `appointment.schedule` (medium), `prescription.renew` (high), `records.access` (critical).

#### Scenario: Medical records are critical risk
- **WHEN** `risk_level("records.access")` is called
- **THEN** it SHALL return "critical"
