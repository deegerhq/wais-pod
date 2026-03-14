"""Google OAuth authentication."""

from __future__ import annotations

import os
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.config import Config

from pod_platform import models

oauth = OAuth()


def setup_oauth():
    """Register Google OAuth provider."""
    oauth.register(
        name="google",
        client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def get_current_user(request: Request) -> Optional[dict]:
    """Get the current user from session, or None.

    If the session has a valid email but the in-memory user record was
    lost (e.g. after a server reload), re-create a minimal user record
    so the session remains usable without forcing a new OAuth login.
    """
    email = request.session.get("user_email")
    if not email:
        return None
    user = models.get_user(email)
    if user is None:
        user = models.upsert_user(email=email, name=email)
    return user
