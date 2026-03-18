## ADDED Requirements

### Requirement: Education vertical scopes
The system SHALL define scopes for education interactions: `course.browse` (low), `course.enroll` (high), `course.drop` (high), `assignment.submit` (high), `grades.access` (medium), `certificate.request` (medium).

#### Scenario: Course browsing is low risk
- **WHEN** `risk_level("course.browse")` is called
- **THEN** it SHALL return "low"

#### Scenario: Course enrollment is high risk
- **WHEN** `risk_level("course.enroll")` is called
- **THEN** it SHALL return "high"

#### Scenario: Course drop is high risk
- **WHEN** `risk_level("course.drop")` is called
- **THEN** it SHALL return "high"

#### Scenario: Assignment submission is high risk
- **WHEN** `risk_level("assignment.submit")` is called
- **THEN** it SHALL return "high"

#### Scenario: Grade access is medium risk
- **WHEN** `risk_level("grades.access")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Certificate request is medium risk
- **WHEN** `risk_level("certificate.request")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Education read-only convenience
- **WHEN** `education_read()` is called
- **THEN** it SHALL return ["course.browse", "grades.access"]

#### Scenario: Education full convenience
- **WHEN** `education_full()` is called
- **THEN** it SHALL return all education scopes

### Requirement: Real Estate vertical scopes
The system SHALL define scopes for real estate interactions: `listing.browse` (low), `listing.compare` (low), `tour.schedule` (medium), `application.submit` (high), `lease.sign` (critical), `maintenance.request` (medium).

#### Scenario: Listing browsing is low risk
- **WHEN** `risk_level("listing.browse")` is called
- **THEN** it SHALL return "low"

#### Scenario: Listing comparison is low risk
- **WHEN** `risk_level("listing.compare")` is called
- **THEN** it SHALL return "low"

#### Scenario: Tour scheduling is medium risk
- **WHEN** `risk_level("tour.schedule")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Application submission is high risk
- **WHEN** `risk_level("application.submit")` is called
- **THEN** it SHALL return "high"

#### Scenario: Lease signing is critical risk
- **WHEN** `risk_level("lease.sign")` is called
- **THEN** it SHALL return "critical"

#### Scenario: Maintenance request is medium risk
- **WHEN** `risk_level("maintenance.request")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Real estate full convenience
- **WHEN** `realestate_full()` is called
- **THEN** it SHALL return all real estate scopes

### Requirement: Social Media and Content vertical scopes
The system SHALL define scopes for social media interactions: `content.read` (low), `content.create` (medium), `content.delete` (high), `profile.modify` (medium), `messaging.read` (medium), `messaging.send` (high), `account.settings` (high).

#### Scenario: Content reading is low risk
- **WHEN** `risk_level("content.read")` is called
- **THEN** it SHALL return "low"

#### Scenario: Content creation is medium risk
- **WHEN** `risk_level("content.create")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Content deletion is high risk
- **WHEN** `risk_level("content.delete")` is called
- **THEN** it SHALL return "high"

#### Scenario: Profile modification is medium risk
- **WHEN** `risk_level("profile.modify")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Message reading is medium risk
- **WHEN** `risk_level("messaging.read")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Message sending is high risk
- **WHEN** `risk_level("messaging.send")` is called
- **THEN** it SHALL return "high"

#### Scenario: Account settings is high risk
- **WHEN** `risk_level("account.settings")` is called
- **THEN** it SHALL return "high"

#### Scenario: Social media full convenience
- **WHEN** `social_full()` is called
- **THEN** it SHALL return all social media scopes

### Requirement: IoT and Smart Home vertical scopes
The system SHALL define scopes for IoT interactions: `device.read` (low), `device.control` (medium), `automation.manage` (high), `firmware.update` (high), `access.grant` (critical), `device.remove` (high).

#### Scenario: Device reading is low risk
- **WHEN** `risk_level("device.read")` is called
- **THEN** it SHALL return "low"

#### Scenario: Device control is medium risk
- **WHEN** `risk_level("device.control")` is called
- **THEN** it SHALL return "medium"

#### Scenario: Automation management is high risk
- **WHEN** `risk_level("automation.manage")` is called
- **THEN** it SHALL return "high"

#### Scenario: Firmware update is high risk
- **WHEN** `risk_level("firmware.update")` is called
- **THEN** it SHALL return "high"

#### Scenario: Access grant is critical risk
- **WHEN** `risk_level("access.grant")` is called
- **THEN** it SHALL return "critical"

#### Scenario: Device removal is high risk
- **WHEN** `risk_level("device.remove")` is called
- **THEN** it SHALL return "high"

#### Scenario: IoT full convenience
- **WHEN** `iot_full()` is called
- **THEN** it SHALL return all IoT scopes
