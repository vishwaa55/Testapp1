import base64
import hashlib
import hmac
import json
import time
from typing import Optional

SECRET_KEY = "dev-secret-key-123"
TOKEN_EXPIRY_SECONDS = 3600


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return hash_password(plain_password) == hashed_password


def create_access_token(user_id: int, username: str, role: str = "user") -> str:
    """Create a signed bearer token for the authenticated user."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8")
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{signature}"


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a signed bearer token."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
        return payload
    except Exception:
        return None


def refresh_access_token(token: str) -> Optional[str]:
    """Issue a fresh token if the current token is valid."""
    payload = decode_access_token(token)
    if not payload:
        return None
    expires_at = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY_SECONDS)
    payload["exp"] = int(expires_at.timestamp())
    return create_access_token(int(payload["sub"]), payload["username"], payload.get("role", "user"))

