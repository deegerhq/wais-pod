# WAIS — Web Agent Interaction Standard

**Specification Draft v0.1**
February 2026

> **DRAFT — For Review and Feedback**

*An open standard for enabling AI agents to interact with, transact on, and complete actions on websites on behalf of authenticated human users.*

---

## 1. Executive Summary

The Web Agent Interaction Standard (WAIS) defines how websites can expose transactional capabilities to AI agents acting on behalf of authenticated human users. While existing standards like `llms.txt` focus on content discoverability and readability, WAIS addresses the next frontier: enabling agents to perform actions — purchasing products, submitting forms, managing returns, booking services, and completing multi-step workflows — in a structured, secure, and verifiable way.

WAIS is built on a core principle we call **Proof of Delegation**: an agent does not need to prove it is human. It needs to prove that a real human has delegated it the authority to act.

This document presents the initial specification for community review and feedback. The goal is to establish an open, vendor-neutral standard that benefits websites, agent platforms, and end users equally.

---

## 2. The Problem

### 2.1 The Current State

Today, when an AI agent needs to perform an action on a website on behalf of a user, it must resort to brittle, unreliable methods: headless browser automation, DOM scraping, visual element detection, and heuristic-based form filling. These approaches break frequently, cannot handle CAPTCHAs, and are indistinguishable from malicious bots.

Meanwhile, websites invest heavily in blocking automated access, creating an adversarial dynamic that hurts both sides: agents cannot reliably serve users, and websites lose potential customers whose agents cannot complete transactions.

### 2.2 The Paradigm Shift

The internet is transitioning from a human-first interface to one where AI agents are primary intermediaries. Users increasingly want to delegate tasks — "buy this list of items," "return this product," "book me a flight" — to agents that act on their behalf. Websites that make this easy will capture this traffic. Those that don't will become invisible to an entire channel of commerce.

WAIS provides the bridge: a structured way for websites to welcome verified agents and for agents to prove they act with legitimate human authorization.

### 2.3 What Exists Today

Several standards address parts of this problem, but none covers the full interaction lifecycle:

| Standard | Focus | Gap |
|----------|-------|-----|
| `llms.txt` | Content discoverability for LLMs | Read-only; no actions, no auth |
| `robots.txt` | Crawler access permissions | Binary allow/block; no interaction |
| Schema.org | Structured data markup | Descriptive, not actionable |
| OAuth 2.0 | User authorization for apps | Designed for apps, not agents |
| OpenAPI | API specification | Assumes dedicated API; most sites lack one |

WAIS fills the gap by defining how agents discover, authenticate, and execute actions on any website, whether it has an API or not.

---

## 3. Core Principles

1. **Proof of Delegation over Proof of Humanity.** Agents don't prove they're human. They prove a human authorized them.
2. **Progressive Capability.** Sites can adopt WAIS incrementally — from a simple manifest to full transactional support.
3. **Human in the Loop.** High-risk actions always require explicit user confirmation. The standard defines when and how.
4. **Open and Vendor-Neutral.** No single agent platform or website technology should be required.
5. **Security by Default.** All agent interactions must be authenticated, scoped, and auditable.
6. **Privacy Preserving.** Sites can verify agent authorization without knowing the user's identity.

---

## 4. Architecture Overview

### 4.1 The Three Parties

Every WAIS interaction involves three entities:

- **The User** — A real human who wants to accomplish a task.
- **The Agent** — An AI system acting on behalf of the user (e.g., Claude, ChatGPT, a custom agent).
- **The Site** — A website or web service that offers actions the agent can perform.

### 4.2 Interaction Flow

The standard interaction flow follows five phases:

| # | Phase | Description |
|---|-------|-------------|
| 1 | **Discovery** | Agent fetches the site's `agents.json` manifest to learn what actions are available. |
| 2 | **Authentication** | Agent presents its Proof of Delegation token, identifying itself, its platform, and the user's authorization scope. |
| 3 | **Execution** | Agent invokes declared actions using the schemas defined in the manifest. |
| 4 | **Confirmation** | For actions above the defined risk threshold, the site returns a confirmation challenge that the agent must present to the user for approval. |
| 5 | **Reporting** | Site returns structured results that the agent can interpret and present to the user. |

---

## 5. The Manifest: `agents.json`

### 5.1 Overview

The `agents.json` file is the entry point for WAIS. Placed at the root of a website (e.g., `https://example.com/agents.json`), it declares what an agent can do on the site, how to authenticate, and what confirmation requirements exist for each action.

### 5.2 Structure

A minimal `agents.json` file:

```json
{
  "wais_version": "0.1",
  "site": {
    "name": "ExampleStore",
    "description": "Online electronics retailer",
    "support_contact": "agents@example.com"
  },
  "authentication": {
    "methods": ["wais-delegation-token"],
    "token_endpoint": "/wais/auth/verify"
  },
  "actions": [
    {
      "id": "search_products",
      "description": "Search product catalog",
      "endpoint": "/wais/api/products/search",
      "method": "POST",
      "risk_level": "low",
      "requires_confirmation": false,
      "input_schema": { "..." : "..." },
      "output_schema": { "..." : "..." }
    },
    {
      "id": "checkout",
      "description": "Complete purchase",
      "endpoint": "/wais/api/checkout",
      "method": "POST",
      "risk_level": "high",
      "requires_confirmation": true,
      "confirmation_details": [
        "total_amount",
        "items",
        "shipping_address",
        "estimated_delivery"
      ],
      "input_schema": { "..." : "..." },
      "output_schema": { "..." : "..." }
    }
  ]
}
```

### 5.3 Action Risk Levels

| Level | Description | Examples |
|-------|-------------|----------|
| `low` | Read-only or reversible actions with no financial impact | Search products, view order status, browse catalog |
| `medium` | Reversible actions or low financial commitment | Add to cart, save to wishlist, update profile, initiate return |
| `high` | Irreversible actions or significant financial commitment | Complete purchase, cancel subscription, submit legal forms |
| `critical` | High-value actions requiring strong user authentication | Large transactions, contract signing, delete account |

---

## 6. Proof of Delegation Protocol

### 6.1 Concept

Proof of Delegation (PoD) is the authentication mechanism at the heart of WAIS. It inverts the traditional web security model: instead of proving a visitor is human, PoD proves that an automated agent has been explicitly authorized by a real human to act within defined boundaries.

### 6.2 The Delegation Token

A Delegation Token is a cryptographically signed credential that encodes:

1. **Agent Identity** — Who is this agent? A verifiable identifier tied to the agent platform (e.g., Anthropic, OpenAI, a registered independent agent).
2. **User Authorization** — Proof that a real human consented to this delegation. The user's identity can remain anonymous to the site — only the fact of authorization needs verification.
3. **Scope** — What actions is this agent authorized to perform? Scopes are granular and follow a standard taxonomy (e.g., `catalog.browse`, `cart.modify`, `checkout.execute`, `return.initiate`).
4. **Constraints** — Limits on the delegation (e.g., maximum transaction amount, time validity, geographic restrictions).
5. **Platform Signature** — Cryptographic signature from the agent's platform, verifiable via public key infrastructure.

### 6.3 Token Structure (Simplified)

The delegation token uses a JWT-like structure:

```json
{
  "header": {
    "alg": "ES256",
    "typ": "WAIS-PoD",
    "kid": "anthropic-agent-key-2026-02"
  },
  "payload": {
    "iss": "https://anthropic.com",
    "sub": "agent:claude-session-abc123",
    "aud": "https://example-store.com",
    "iat": 1708617600,
    "exp": 1708621200,
    "delegation": {
      "user_hash": "sha256:a1b2c3...",
      "user_verified": true,
      "consent_timestamp": 1708617500,
      "scopes": [
        "catalog.browse",
        "cart.modify",
        "checkout.execute"
      ],
      "constraints": {
        "max_transaction_amount": {
          "value": 500,
          "currency": "EUR"
        },
        "require_confirmation_above": {
          "value": 100,
          "currency": "EUR"
        }
      }
    }
  },
  "signature": "base64url-encoded-signature"
}
```

### 6.4 Verification Flow

When an agent presents a PoD token to a site:

1. The site validates the token signature against the agent platform's published public key.
2. The site checks that the token hasn't expired and that the audience matches its domain.
3. The site verifies that the requested action falls within the token's declared scopes.
4. If the action exceeds constraints (e.g., amount over threshold), the site returns a confirmation challenge.

No CAPTCHAs. No browser fingerprinting. Trust is established cryptographically.

### 6.5 Distinguishing Agents from Bots

A key benefit of PoD is that it cleanly separates legitimate agents from malicious bots:

| Property | WAIS Agent | Malicious Bot |
|----------|------------|---------------|
| Delegation token | Valid, signed by known platform | Absent or forged |
| Scoped permissions | Granular, declared in advance | Attempts everything |
| User behind it | Verified human (hashed) | No user linkage |
| Confirmation flow | Supports challenge-response | Cannot complete |
| Audit trail | Full traceability | None |

---

## 7. Confirmation Protocol

### 7.1 When Confirmation Is Required

The site defines confirmation requirements per action in `agents.json`. WAIS recommends the following defaults, which sites can customize:

| Risk Level | Behavior | Description |
|------------|----------|-------------|
| **Low** | No confirmation required | Agent can execute freely. |
| **Medium** | Soft confirmation | Agent must present action details to user before proceeding. |
| **High** | Hard confirmation | Site generates a challenge; user must approve via their agent platform. |
| **Critical** | Strong authentication | User must authenticate directly (biometric, PIN, 2FA) through their agent platform. |

### 7.2 Confirmation Challenge Structure

When a site requires confirmation, it responds to the agent with a structured challenge:

```json
{
  "wais_confirmation": {
    "challenge_id": "conf_abc123",
    "action": "checkout",
    "risk_level": "high",
    "expires_at": "2026-02-22T15:30:00Z",
    "display_to_user": {
      "summary": "Purchase 3 items from ExampleStore",
      "total": "€247.50",
      "items": [
        "Sony WH-1000XM5 Headphones - €189.00",
        "USB-C Cable 2-pack - €12.50",
        "Screen Protector - €46.00"
      ],
      "shipping": "Standard (3-5 business days)",
      "payment_method": "Visa ending 4242"
    },
    "approval_methods": ["user_confirm", "biometric"]
  }
}
```

The agent's platform presents this to the user in its own interface, collects approval, and returns a signed confirmation response to the site.

---

## 8. Standard Scopes by Vertical

WAIS defines a taxonomy of scopes to ensure consistency across implementations. Sites declare which scopes they support; agents request only what they need.

### 8.1 E-Commerce

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `catalog.browse` | Search and view products | Low |
| `catalog.compare` | Access pricing and availability for comparison | Low |
| `cart.modify` | Add/remove items from cart | Medium |
| `checkout.execute` | Complete a purchase | High |
| `order.track` | View order status and tracking | Low |
| `return.initiate` | Start a return or exchange | Medium |
| `return.complete` | Complete return process (label, pickup) | High |
| `subscription.manage` | Modify or cancel subscriptions | High |

### 8.2 Travel & Hospitality

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `availability.search` | Search flights, hotels, restaurants | Low |
| `booking.create` | Make a reservation | High |
| `booking.modify` | Change dates, seats, rooms | High |
| `booking.cancel` | Cancel a reservation | High |
| `claim.submit` | File compensation claims | Medium |

### 8.3 Financial Services

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `account.read` | View balances and transactions | Medium |
| `quote.request` | Request insurance/loan quotes | Low |
| `payment.execute` | Make a payment or transfer | Critical |
| `dispute.file` | Dispute a charge | Medium |
| `policy.modify` | Change insurance policy details | High |

### 8.4 Government & Public Services

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `appointment.book` | Schedule appointments | Medium |
| `form.submit` | Submit government forms | High |
| `document.request` | Request documents or certificates | High |
| `status.check` | Check application or process status | Low |

### 8.5 Healthcare

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `appointment.schedule` | Book medical appointments | Medium |
| `prescription.renew` | Request prescription renewals | High |
| `records.access` | Retrieve test results | Critical |

### 8.6 Education

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `course.browse` | Search and view courses or programs | Low |
| `course.enroll` | Enroll in a course or program | High |
| `course.drop` | Drop or withdraw from a course | High |
| `assignment.submit` | Submit coursework or assignments | High |
| `grades.access` | View grades and transcripts | Medium |
| `certificate.request` | Request completion certificates | Medium |

### 8.7 Real Estate

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `listing.browse` | Search properties | Low |
| `listing.compare` | Access detailed pricing and history | Low |
| `tour.schedule` | Schedule property viewings | Medium |
| `application.submit` | Submit rental or purchase applications | High |
| `lease.sign` | Sign a lease or agreement | Critical |
| `maintenance.request` | Submit maintenance requests | Medium |

### 8.8 Social Media & Content

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `content.read` | Browse feeds and profiles | Low |
| `content.create` | Create posts or comments | Medium |
| `content.delete` | Delete own content | High |
| `profile.modify` | Update profile information | Medium |
| `messaging.read` | Read messages and notifications | Medium |
| `messaging.send` | Send messages | High |
| `account.settings` | Modify account settings | High |

### 8.9 IoT & Smart Home

| Scope | Allows | Risk Level |
|-------|--------|------------|
| `device.read` | View device status and sensor data | Low |
| `device.control` | Control devices (on/off, adjust) | Medium |
| `automation.manage` | Create or modify automation rules | High |
| `firmware.update` | Trigger firmware updates | High |
| `access.grant` | Grant device access to others | Critical |
| `device.remove` | Remove or unpair a device | High |

---

## 9. Use Cases in Detail

### 9.1 Agent-Powered Shopping

A user tells their agent: *"Prepare a list of supplies for my camping trip and buy everything for under €300."*

The agent:

1. Searches multiple WAIS-compliant outdoor stores simultaneously (`catalog.browse`).
2. Compares prices and availability (`catalog.compare`).
3. Builds an optimized cart across the best-priced stores.
4. Presents a consolidated summary to the user: *"Found everything across 2 stores for €267. Confirm?"*
5. Upon user approval, executes checkout at each store (`checkout.execute` with confirmation protocol).

Post-purchase, the agent monitors order status (`order.track`) and if any item arrives damaged, initiates a return (`return.initiate`) and schedules a pickup (`return.complete`) — all without the user visiting a single website.

### 9.2 Travel Disruption Management

A user's flight gets cancelled. Their agent automatically:

1. Detects the cancellation via the airline's status endpoint.
2. Searches alternative flights (`availability.search`) across multiple airlines.
3. Books the best option within the user's preferences (`booking.create` with confirmation).
4. Adjusts the hotel reservation dates (`booking.modify`).
5. Files an EU261 compensation claim (`claim.submit`).

All within minutes, presenting each decision to the user for approval.

### 9.3 Subscription Audit

A user asks: *"Review all my subscriptions and cancel anything I haven't used in 3 months."*

The agent accesses each subscription service (`account.read`), checks usage data, presents a report to the user, and upon approval, cancels the unused ones (`subscription.manage` with confirmation for each). Dark patterns that hide cancellation flows become irrelevant because the agent interacts via the structured WAIS endpoint, not the UI.

### 9.4 Government Bureaucracy

A user needs to renew their driver's license. The agent:

1. Checks eligibility and requirements (`status.check`).
2. Fills out the renewal form with the user's stored data (`form.submit` with critical confirmation).
3. Uploads required documents.
4. Books an appointment if an in-person visit is needed (`appointment.book`).
5. Tracks the application status.

Turning a multi-hour bureaucratic process into a 2-minute interaction.

### 9.5 Continuing Education

A user tells their agent: *"Find me a Python data science course under $50, enroll me, and track my deadlines."*

The agent:

1. Searches multiple WAIS-compliant education platforms (`course.browse`).
2. Compares course ratings, prices, and schedules.
3. Presents the top options to the user for selection.
4. Upon approval, enrolls the user in the chosen course (`course.enroll` with confirmation).
5. Monitors assignment deadlines and submits completed coursework (`assignment.submit` with confirmation).
6. Checks grades as they're posted (`grades.access`).
7. Requests the completion certificate when the course is finished (`certificate.request`).

The user completes an entire learning journey without navigating a single platform UI.

### 9.6 Apartment Hunting

A user asks: *"Find me a 2-bedroom apartment near downtown under $2000/month and schedule tours for the top 3."*

The agent:

1. Searches multiple rental platforms simultaneously (`listing.browse`).
2. Compares pricing, amenities, and neighborhood data (`listing.compare`).
3. Filters results by the user's criteria and ranks them.
4. Presents the shortlist: *"Found 12 options, here are the top 3. Schedule tours?"*
5. Upon approval, schedules viewings for each (`tour.schedule` with confirmation).
6. After the user selects a unit, submits the rental application (`application.submit` with confirmation).
7. When approved, presents the lease for the user to sign (`lease.sign` with critical confirmation).

Post-move-in, the agent can submit maintenance requests (`maintenance.request`) when issues arise.

### 9.7 Social Media Management

A user says: *"Post my product launch announcement across all my social channels."*

The agent:

1. Reads the user's profile information across platforms (`content.read`).
2. Drafts platform-appropriate versions of the announcement.
3. Presents all drafts for user review: *"Here are your posts for Twitter, LinkedIn, and Instagram. Approve?"*
4. Upon approval, publishes each post (`content.create` with confirmation).
5. Monitors responses and messages (`messaging.read`).
6. Flags important messages that need the user's direct reply.

If the user later wants to remove a post, the agent handles deletion (`content.delete` with confirmation) across all platforms in one action.

### 9.8 Smart Home Automation

A user says: *"Set my home to vacation mode — lower the thermostat, turn on random lights, and lock all doors."*

The agent:

1. Reads current device states across the smart home system (`device.read`).
2. Presents the proposed changes: *"I'll set thermostat to 15°C, enable random light schedule, and lock 3 doors. Confirm?"*
3. Upon approval, adjusts each device (`device.control` with confirmation).
4. Creates an automation rule to randomize lights daily (`automation.manage` with confirmation).
5. Monitors device status for anomalies while the user is away.

No new access is granted to others (`access.grant` is not requested), keeping the home secure. When the user returns, the agent reverses the changes in one command.

---

## 10. Adoption Path

### 10.1 Progressive Implementation

WAIS is designed for incremental adoption. Sites can start minimal and expand:

**Level 1: Manifest Only**
Publish `agents.json` with read-only actions (search, browse, status). Zero backend changes required if the site already has any kind of API. This alone makes the site discoverable to agents.

**Level 2: Basic Interactions**
Add medium-risk actions (add to cart, update preferences). Implement PoD token verification. The site now supports assisted workflows where agents prepare actions for users.

**Level 3: Full Transactions**
Enable high-risk actions (checkout, returns, cancellations) with the confirmation protocol. This is the full WAIS experience where agents can complete end-to-end workflows.

**Level 4: Proactive Integration**
Implement webhooks and event streams so agents can react to changes (order shipped, price drop, booking cancelled). The site becomes a fully agent-native platform.

### 10.2 Incentive Structure

The adoption incentive is competitive pressure, not regulation. The first e-commerce site in a category to implement WAIS captures agent-driven traffic that competitors cannot serve. As more users delegate shopping to agents, non-WAIS sites lose a growing channel.

This mirrors the early days of e-commerce: the first retailers to accept online payments captured demand that brick-and-mortar stores could not. WAIS is the "accept online payments" moment for the agent era.

---

## 11. Security Considerations

1. **Token Expiration** — All PoD tokens must have a short TTL (recommended: 1 hour max). Long-lived delegations should use refresh mechanisms.
2. **Scope Minimization** — Agents should request the minimum scopes needed. Sites should reject over-scoped tokens.
3. **Replay Protection** — Tokens should include a nonce and be bound to a specific session.
4. **Rate Limiting** — Sites should implement per-agent rate limits separate from human rate limits.
5. **Audit Logging** — All agent actions must be logged with the agent's identity and delegation context for accountability.
6. **Revocation** — Users must be able to revoke agent permissions at any time via their agent platform. Sites should support token revocation checks.

   **Revocation List Protocol:** Agent platforms MUST publish a JSON revocation list at `/.well-known/wais-revocation` containing all currently revoked tokens that have not yet expired. The list format is:

   ```json
   {
     "version": 1,
     "issuer": "https://agent-platform.com",
     "published_at": 1708617600,
     "ttl_seconds": 300,
     "entries": [
       {
         "jti": "token-uuid",
         "revoked_at": 1708617500,
         "reason": "user_revoked"
       }
     ]
   }
   ```

   - **`ttl_seconds`**: Cache duration (60–300 seconds). Websites SHOULD re-fetch the list after this period.
   - **`reason`**: One of `user_revoked`, `platform_revoked`, `compromised`, or `superseded`.
   - **Pruning**: Entries for tokens past their `exp` timestamp MAY be removed, as expired tokens are already rejected by the verifier.
   - **Verification**: Websites that support revocation checking SHOULD fetch the revocation list from the issuing platform periodically and reject tokens whose `jti` appears in the list. Revocation checking is opt-in — verifiers without a configured revocation list continue to operate as before.
   - **Recommendation**: Use short token lifetimes (5–10 minutes) to minimize the window between revocation and enforcement.
7. **Platform Registry** — A public registry of trusted agent platforms and their public keys enables sites to verify agent identities.

---

## 12. What Comes Next

### 12.1 Immediate Next Steps

1. Community review and feedback on this draft specification.
2. Reference implementation of `agents.json` validator and PoD token library.
3. Proof-of-concept integration with one e-commerce platform.
4. Formal JSON Schema definitions for `agents.json` and PoD tokens.
5. Open-source audit tool that scans sites for WAIS compliance.

### 12.2 Open Questions

Several design decisions require community input:

- Should the Platform Registry be centralized (like a CA system) or decentralized (like DNS)?
- How should WAIS interact with existing authentication flows (OAuth, SAML, passkeys)?
- What governance model should manage the standard's evolution?
- How should WAIS handle sites that require user accounts vs. guest checkout?
- Should there be a WAIS compliance certification program?

---

## 13. Get Involved

WAIS is an open initiative. We are seeking feedback from web developers, e-commerce platforms, AI agent builders, security researchers, and anyone who believes the future of the web involves agents acting on behalf of humans.

If your website wants to be where agents shop, book, file, and transact in the agent era, WAIS is how you open that door.

---

> *The web spent 20 years building walls against bots pretending to be human. The next era is about welcoming agents that prove a human trusts them.*
