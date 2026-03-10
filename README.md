# Proof of Delegation (PoD)

> **The future isn't about proving you're human. It's about proving a human trusts you.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Standard: WAIS](https://img.shields.io/badge/Standard-WAIS_v0.1-1B4F72.svg)](https://deeger.io)
[![Status: Draft](https://img.shields.io/badge/Status-Draft-orange.svg)]()

**Proof of Delegation (PoD)** is an open-source authentication protocol that enables AI agents to prove they are acting on behalf of a real human user — with verifiable, scoped, and time-limited authorization.

PoD is the authentication layer of the [WAIS (Web Agent Interaction Standard)](https://deeger.io/wais) initiative by [Deeger](https://deeger.io).

---

## The Problem

Today's web authentication is built around one question: **"Are you human?"** — CAPTCHAs, browser fingerprinting, behavioral analysis.

But as AI agents become the primary way people interact with the web, the question changes:

> **"Does a human trust you to act on their behalf?"**

No existing standard answers this cleanly:

| Standard | What it proves | What it doesn't |
|----------|---------------|-----------------|
| CAPTCHA | Visitor is human | Nothing about agents |
| OAuth 2.0 | User authorized an app | Not designed for autonomous agents |
| Web Bot Auth (RFC 9421) | Bot identity is verified | Not who authorized the bot |
| Visa TAP / Mastercard Agent Pay | Payment authorization | Proprietary, vendor-locked |

**PoD fills the gap**: an open, vendor-neutral protocol for proving that an agent has been explicitly delegated authority by an authenticated human user.

---

## How It Works

```
┌──────────┐     1. User delegates        ┌──────────────┐
│          │ ─────authority + scopes────▶ │              │
│   USER   │                              │  AGENT       │
│          │ ◀───4. Confirmation───────── │  PLATFORM    │
│          │     challenge (if needed)    │  (e.g.Claude)│
└──────────┘                              └──────┬───────┘
                                                 │
                                         2. Agent presents
                                            PoD token
                                                 │
                                                 ▼
                                         ┌──────────────┐
                                         │              │
                                         │   WEBSITE    │
                                         │   (e.g.      │
                                         │  e-commerce) │
                                         │              │
                                         └──────┬───────┘
                                                │
                                                ▼
                                         3. Site verifies
                                            token signature,
                                            scopes, constraints
```

### The Flow

1. **User delegates**: The user, through their agent platform, authorizes an agent to act within specific scopes and constraints.
2. **Agent presents token**: The agent sends a cryptographically signed PoD token with every request to a website.
3. **Site verifies**: The site validates the token signature against the agent platform's public key, checks scopes and constraints.
4. **Confirmation (conditional)**: For high-risk actions, the site sends a confirmation challenge back through the agent to the user.

No CAPTCHAs. No browser fingerprinting. Trust established cryptographically.

---

## The PoD Token

A PoD token is a JWT-like credential with three key sections:

```json
{
  "header": {
    "alg": "ES256",
    "typ": "WAIS-PoD",
    "kid": "platform-key-2026-02"
  },
  "payload": {
    "iss": "https://agent-platform.example.com",
    "sub": "agent:session-abc123",
    "aud": "https://target-website.com",
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

### Key Properties

- **Privacy-preserving**: The `user_hash` proves a real user exists without revealing their identity.
- **Scoped**: Agents can only do what the user explicitly authorized.
- **Constrained**: Financial limits, time limits, geographic restrictions.
- **Short-lived**: Tokens expire quickly (recommended: 1 hour max).
- **Verifiable**: Sites verify signatures against the platform's published public key.

---

## Standard Scopes

PoD defines a taxonomy of scopes by vertical:

### E-Commerce
| Scope | Description | Risk Level |
|-------|-------------|------------|
| `catalog.browse` | Search and view products | Low |
| `catalog.compare` | Access pricing for comparison | Low |
| `cart.modify` | Add/remove cart items | Medium |
| `checkout.execute` | Complete a purchase | High |
| `order.track` | View order status | Low |
| `return.initiate` | Start a return | Medium |
| `return.complete` | Complete return (label, pickup) | High |
| `subscription.manage` | Modify/cancel subscriptions | High |

### Travel & Hospitality
| Scope | Description | Risk Level |
|-------|-------------|------------|
| `availability.search` | Search flights, hotels | Low |
| `booking.create` | Make a reservation | High |
| `booking.modify` | Change reservation details | High |
| `booking.cancel` | Cancel a reservation | High |
| `claim.submit` | File compensation claims | Medium |

### Financial Services
| Scope | Description | Risk Level |
|-------|-------------|------------|
| `account.read` | View balances/transactions | Medium |
| `quote.request` | Request quotes | Low |
| `payment.execute` | Make a payment | Critical |
| `dispute.file` | Dispute a charge | Medium |

### Government & Healthcare
| Scope | Description | Risk Level |
|-------|-------------|------------|
| `appointment.book` | Schedule appointments | Medium |
| `form.submit` | Submit forms | High |
| `document.request` | Request documents | High |
| `records.access` | Access medical records | Critical |

---

## Confirmation Protocol

For high-risk actions, the site returns a **confirmation challenge**:

```json
{
  "wais_confirmation": {
    "challenge_id": "conf_abc123",
    "action": "checkout",
    "risk_level": "high",
    "expires_at": "2026-02-26T15:30:00Z",
    "display_to_user": {
      "summary": "Purchase 3 items from ExampleStore",
      "total": "€247.50",
      "items": [
        "Sony WH-1000XM5 - €189.00",
        "USB-C Cable 2-pack - €12.50",
        "Screen Protector - €46.00"
      ],
      "shipping": "Standard (3-5 days)",
      "payment_method": "Visa ending 4242"
    },
    "approval_methods": ["user_confirm", "biometric"]
  }
}
```

The agent's platform presents this to the user, collects approval, and returns a signed confirmation.

### Risk Levels

| Level | Behavior | Examples |
|-------|----------|---------|
| **Low** | No confirmation needed | Browse, search, check status |
| **Medium** | Soft confirmation | Add to cart, update profile |
| **High** | Hard confirmation required | Purchase, cancel subscription |
| **Critical** | Strong authentication (biometric/2FA) | Large payments, legal forms |

---

## Quick Start — MVP Demo

### 1. Install

```bash
git clone https://github.com/deegerhq/wais-pod.git
cd wais-pod
python -m venv .venv && source .venv/bin/activate
make install
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your Google OAuth credentials (optional for API-only usage)
```

### 3. Run the Platform (Token Issuer) — `:8000`

```bash
make platform
# Open http://localhost:8000 — Sign in with Google, create delegation tokens
```

### 4. Run the Demo Store (Verifier) — `:8001`

```bash
make store
# Open http://localhost:8001 — Browse the product catalog
```

### 5. Test the Full Flow with curl

```bash
# Browse catalog (public)
curl http://localhost:8001/api/products

# With a PoD token (get one from the platform dashboard):
TOKEN="eyJ..."

# Add to cart
curl -X POST http://localhost:8001/api/cart \
  -H "X-WAIS-PoD: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"headphones-1","quantity":1}'

# Checkout (may require confirmation if total > threshold)
curl -X POST http://localhost:8001/api/checkout \
  -H "X-WAIS-PoD: $TOKEN"
```

### 6. MCP Server (for Claude Desktop)

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "wais-pod-demo": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/wais-pod",
      "env": {
        "POD_TOKEN": "eyJ...",
        "STORE_URL": "http://localhost:8001"
      }
    }
  }
}
```

Then ask Claude: *"Browse the demo store and buy me some headphones"*

### 7. Run Tests

```bash
make test
```

---

## Library Usage

### Verify a PoD Token (Site-side)

```python
from pod import PoDVerifier

verifier = PoDVerifier()
verifier.add_trusted_platform_pem("https://platform.example.com", public_key_pem)

result = verifier.verify(
    token_string,
    required_scopes=["checkout.execute"],
    expected_audience="https://your-site.com",
)

if result.valid:
    if result.requires_confirmation(action_amount=247.50):
        return confirmation_challenge(...)
    else:
        process_order(...)
else:
    return {"error": result.reason}, 403
```

### Issue a PoD Token (Agent Platform-side)

```python
from pod import PoDIssuer

issuer = PoDIssuer(private_key_path="./keys/platform.pem")

token = issuer.create_token(
    agent_session="session-abc123",
    audience="https://example-store.com",
    user_hash="sha256:a1b2c3...",
    scopes=["catalog.browse", "cart.modify", "checkout.execute"],
    constraints={
        "max_transaction_amount": {"value": 500, "currency": "EUR"},
        "require_confirmation_above": {"value": 100, "currency": "EUR"},
    },
    ttl_seconds=3600,
)
```

---

## Agents vs. Bots: How PoD Differentiates

| Property | WAIS Agent with PoD | Malicious Bot |
|----------|-------------------|---------------|
| Delegation token | Valid, signed by known platform | Absent or forged |
| Scoped permissions | Granular, declared in advance | Attempts everything |
| User behind it | Verified human (hashed) | No user linkage |
| Confirmation flow | Supports challenge-response | Cannot complete |
| Audit trail | Full traceability | None |

---

## Design Principles

1. **Proof of Delegation over Proof of Humanity** — Agents prove authorization, not species.
2. **Open and Vendor-Neutral** — No vendor lock-in. Built on open standards (JWT, ES256, RFC 9421).
3. **Privacy Preserving** — Sites verify authorization without knowing the user's identity.
4. **Security by Default** — Short-lived tokens, minimal scopes, mandatory audit trails.
5. **Progressive Adoption** — Works with or without existing auth infrastructure.
6. **Complementary** — Designed to work alongside Web Bot Auth, OAuth 2.0, MCP, and A2A.

---

## Compatibility

PoD is designed to complement, not replace, existing protocols:

- **Web Bot Auth (RFC 9421)**: PoD adds the *delegation* layer on top of agent identity verification.
- **OAuth 2.0**: PoD extends the delegation concept specifically for autonomous agents.
- **A2A (Google)**: Agent-to-agent communication can include PoD tokens for user authorization.
- **MCP (Anthropic)**: MCP tools can verify PoD tokens before executing actions.
- **ARA / agents.json**: Manifests declare actions; PoD authorizes agents to execute them.

---

## Roadmap

- [x] Specification draft v0.1
- [x] Python reference implementation (core library)
- [x] MVP: Platform (issuer), Demo Store (verifier), MCP Server
- [ ] Node.js reference implementation
- [ ] Go reference implementation
- [ ] Open Platform Registry for public key discovery
- [ ] WAIS Lighthouse audit tool
- [ ] Pilot integration with e-commerce platform
- [ ] Formal JSON Schema definitions
- [ ] Security audit

---

## Part of the WAIS Ecosystem

PoD is the authentication layer of **WAIS (Web Agent Interaction Standard)** — an open standard for enabling AI agents to interact with, transact on, and complete actions on websites on behalf of authenticated human users.

WAIS includes:
- **`agents.json`** — Manifest declaring what agents can do on a site
- **Proof of Delegation** — Authentication protocol (this repo)
- **Confirmation Protocol** — Human-in-the-loop for high-risk actions
- **WAIS Lighthouse** — Audit tool for agent-readiness scoring

Learn more at [deeger.io](https://deeger.io).

---

## Contributing

We welcome contributions! This is an early-stage open standard and every perspective matters.

- **Spec feedback**: Open an issue with the `spec` label
- **Implementation**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: Report vulnerabilities to security@deeger.io

---

## Support the Project

PoD and WAIS are open-source initiatives by [Deeger](https://deeger.io). If you believe in an open, agent-friendly web:

- ⭐ Star this repo
- 🗣️ Share with your network
- 💰 [Sponsor the project](https://deeger.io/sponsor)

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built by <a href="https://deeger.io">Deeger</a></strong><br/>
  <em>Agents need the real web.</em>
</p>
