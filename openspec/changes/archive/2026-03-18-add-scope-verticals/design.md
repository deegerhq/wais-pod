## Context

PoD's scope taxonomy currently defines 5 verticals (E-Commerce, Travel, Finance, Government, Healthcare) across 3 files that must stay in sync: `pod/scopes.py` (source of truth), `spec/WAIS-Spec-Draft-v0.1.md` (formal spec), and `README.md` (public docs). Each vertical follows an identical pattern: scope constants, risk level mappings, and optional convenience methods.

This change adds 4 new verticals (Education, Real Estate, Social Media, IoT) following the exact same patterns. No architectural changes are needed — this is purely additive.

## Goals / Non-Goals

**Goals:**
- Add 25 new scopes across 4 verticals with consistent naming and risk levels
- Keep all 3 files (code, spec, README) in sync
- Add tests for all new scopes
- Follow existing patterns exactly so the codebase remains uniform

**Non-Goals:**
- No changes to token structure, verification, or confirmation protocol
- No new namespace collision detection (not needed — all new namespaces are unique)
- No changes to the platform server or demo store

## Decisions

### 1. Namespace selection — use domain-specific names, not generic ones

**Decision:** Use namespaces like `course`, `listing`, `content`, `device` rather than generic `edu`, `re`, `social`, `iot` prefixes.

**Why:** Existing verticals use domain nouns (`catalog`, `booking`, `account`), not abbreviations. Keeping the same style avoids a naming inconsistency. Also, `namespace.action` reads naturally: `course.enroll`, `listing.browse`, `device.control`.

**Alternative considered:** Prefix-based (`edu.enroll`, `iot.control`) — rejected because it breaks the established pattern where the namespace is the object being acted on.

### 2. File change order — scopes.py first, then spec, then README

**Decision:** Update `pod/scopes.py` first as the source of truth, then the spec document, then README.

**Why:** Code is testable — we can validate risk levels and convenience methods immediately. The spec and README are documentation of what the code defines. This matches how the existing verticals were built.

### 3. Convenience methods — one read + one full per vertical where applicable

**Decision:** Add `education_read()`, `education_full()`, `realestate_full()`, `social_full()`, `iot_full()`. Only education gets a `_read()` variant (course.browse + grades.access). Other verticals don't have a natural read-only subset.

**Why:** Existing pattern has `ecommerce_read()` / `ecommerce_full()` and `travel_full()`. Not every vertical needs a `_read()` — only add it when there's a meaningful read-only grouping.

### 4. Spec sections — 8.6 through 8.9, use cases 9.5 through 9.8

**Decision:** Number new sections sequentially after existing ones.

**Why:** The spec currently ends at 8.5 (Healthcare) and 9.4 (Government). Sequential numbering is the simplest approach and avoids renumbering.

## File Changes

### `pod/scopes.py`
- Add scope constants for each vertical (UPPER_SNAKE_CASE)
- Add risk level entries to the `RISK_LEVELS` dict
- Add convenience methods: `education_read()`, `education_full()`, `realestate_full()`, `social_full()`, `iot_full()`

### `spec/WAIS-Spec-Draft-v0.1.md`
- Add section 8.6 (Education), 8.7 (Real Estate), 8.8 (Social Media), 8.9 (IoT) with scope tables
- Add section 9.5 (Education use case), 9.6 (Real Estate), 9.7 (Social Media), 9.8 (IoT)

### `README.md`
- Add 4 new vertical tables in the Standard Scopes section, after Healthcare

### `tests/test_scopes.py`
- Add tests for each new scope's risk level
- Add tests for each convenience method's return value
- Add tests confirming `is_high_risk` works for new high/critical scopes

## Risks / Trade-offs

- **[Risk] Namespace collision with future verticals** → Mitigated: chosen namespaces (`course`, `listing`, `content`, `device`, `automation`, `firmware`, `access`, `messaging`, `profile`, `grades`, `certificate`, `tour`, `application`, `lease`, `maintenance`, `assignment`) are specific enough to avoid overlap.
- **[Risk] Spec document grows large** → Acceptable: 4 tables and 4 use cases add ~120 lines, keeping the spec under control.
- **[Trade-off] `account.settings` vs existing `account.read`** → Different verticals can share namespace prefixes because the action suffix differentiates them. `account.read` (finance) and `account.settings` (social) are distinct scopes.
