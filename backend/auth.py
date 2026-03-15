from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def truncate_to_72_bytes(password: str) -> str:
    """
    Truncate a password to a maximum of 72 UTF-8 bytes.
    If the password is already short enough, returns it unchanged.
    """
    encoded = password.encode('utf-8')
    if len(encoded) <= 72:
        return password
    # Truncate and decode, ignoring any incomplete multi-byte characters
    return encoded[:72].decode('utf-8', errors='ignore')

def get_password_hash(password: str) -> str:
    """Hash a password, truncating to 72 bytes first."""
    truncated = truncate_to_72_bytes(password)
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password, truncating to 72 bytes first."""
    truncated = truncate_to_72_bytes(plain_password)
    return pwd_context.verify(truncated, hashed_password)

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength on the original (untruncated) password.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 20:
        return False, "Password must not exceed 20 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta

SECRET_KEY = "your-very-secret-key-change-this"  # use same as session secret
serializer = URLSafeTimedSerializer(SECRET_KEY)

def generate_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token: str, max_age_seconds: int = 3600):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age_seconds)
        return email
    except:
        return None
    from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "your-very-secret-key-change-this"  # use same as session secret
serializer = URLSafeTimedSerializer(SECRET_KEY)

def generate_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token: str, max_age_seconds: int = 3600):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age_seconds)
        return email
    except:
        return None