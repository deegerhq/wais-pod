"""
Proof of Delegation (PoD) - Open-source authentication for AI agents.

An open protocol enabling AI agents to prove they act on behalf of
authenticated human users with verifiable, scoped authorization.

Part of the WAIS (Web Agent Interaction Standard) ecosystem.
https://deeger.io
"""

__version__ = "0.1.0"
__author__ = "Deeger"
__license__ = "MIT"

from pod.token import PoDToken, DelegationPayload, Constraints
from pod.issuer import PoDIssuer
from pod.verifier import PoDVerifier
from pod.confirmation import ConfirmationChallenge, ConfirmationResponse
from pod.scopes import Scopes
from pod.revocation import RevocationList, RevocationEntry

__all__ = [
    "PoDToken",
    "DelegationPayload",
    "Constraints",
    "PoDIssuer",
    "PoDVerifier",
    "ConfirmationChallenge",
    "ConfirmationResponse",
    "Scopes",
    "RevocationList",
    "RevocationEntry",
]
