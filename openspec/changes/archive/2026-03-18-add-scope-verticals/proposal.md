## Why

The current scope taxonomy covers 5 verticals (e-commerce, travel, finance, government, healthcare), but AI agents are increasingly used in education, real estate, social media, and IoT. Without standard scopes for these domains, agent platforms and websites must invent ad-hoc scope names, breaking interoperability. Adding these verticals now — while the spec is still in draft — ensures broad coverage before v1.0 solidifies.

## What Changes

- Add **Education** vertical scopes: course browsing, enrollment, dropping, assignment submission, grade access, certificate requests
- Add **Real Estate** vertical scopes: listing browsing/comparison, tour scheduling, application submission, lease signing, maintenance requests
- Add **Social Media & Content** vertical scopes: content read/create/delete, profile modification, messaging read/send, account settings
- Add **IoT & Smart Home** vertical scopes: device read/control, automation management, firmware updates, access grants, device removal
- Each scope gets a risk level assignment (low/medium/high/critical) justified by reversibility and financial/legal impact
- Convenience methods added for each vertical (e.g., `education_read()`, `realestate_full()`)
- Spec document, README, and code all updated in sync

## Non-goals

- No changes to the token structure, verification logic, or confirmation protocol
- No changes to the platform server or demo store
- No new verticals beyond the 4 proposed (others can follow in separate changes)
- No new dependencies

## Capabilities

### New Capabilities

_(none — no new spec files needed)_

### Modified Capabilities

- `scope-taxonomy`: Adding 4 new vertical sections (Education, Real Estate, Social Media, IoT) with scope definitions, risk levels, and convenience methods

## Impact

- **`pod/scopes.py`** — New scope constants, risk level mappings, convenience methods
- **`spec/WAIS-Spec-Draft-v0.1.md`** — New sections 8.6–8.9 (scope tables) and 9.5–9.8 (use cases)
- **`README.md`** — New vertical tables in the Standard Scopes section
- **`tests/test_scopes.py`** — New tests for risk levels and convenience methods of all 4 verticals
