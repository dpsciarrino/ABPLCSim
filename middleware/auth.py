# middleware/auth.py
#
# Responsibilities:
#   - Validate JWT access tokens on every protected request
#   - Extract user_id from the token payload
#   - Inject user_id into the request state for downstream use by SessionManager
#   - Return HTTP 401 for missing, expired, or invalid tokens
#
# During local development (v0.1.0 – v0.4.0):
#   This module exists as a stub. The get_current_user dependency passes
#   all requests through without validation.
#   The stub is clearly marked and must be replaced before any public deployment.
#
# SECURITY RULE: Do not deploy to PythonAnywhere until this stub is
# replaced with real JWT validation at v0.5.0.
#
# Dependencies: fastapi, python-jose, passlib, db.crud
#
# TODO: Implement create_access_token, verify_token, get_current_user at v0.5.0

async def get_current_user():
    """
    STUB — returns a placeholder user without any token validation.
    Replace with real JWT verification before any public deployment.
    """
    raise NotImplementedError("Auth not yet implemented. Do not deploy publicly.")

