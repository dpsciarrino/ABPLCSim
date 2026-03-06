# middleware/auth.py
#
# Responsibilities:
#   - Validate JWT access tokens on every protected request
#   - Extract user_id from the token payload
#   - Inject user_id into the request state for downstream use by SessionManager
#   - Return HTTP 401 for missing, expired, or invalid tokens
#
# During local development (v0.1.0 – v0.4.0):
#   This middleware exists as a stub that passes all requests through.
#   The stub is clearly marked and must be replaced before any public deployment.
#
# SECURITY RULE: Do not deploy to PythonAnywhere until the stub below is
# replaced with real JWT validation. Deploying with the stub active exposes
# all API routes without authentication.
#
# Dependencies: fastapi, python-jose, db.crud
#
# TODO: Replace stub with real JWT validation at v0.5.0

class AuthMiddleware:
    """
    STUB — passes all requests through without validation.
    Replace with JWT validation before any public deployment.
    """
    pass

