import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _derive_fernet_key() -> bytes:
    """Derive a Fernet key from Django SECRET_KEY or PAYMENT_ENCRYPTION_KEY.

    If PAYMENT_ENCRYPTION_KEY is set (base64 32-byte), use it directly.
    Otherwise derive deterministically from SECRET_KEY so the key survives
    restarts without extra env config. Changing SECRET_KEY will invalidate
    stored keys — rotate via management command if needed.
    """
    custom = getattr(settings, 'PAYMENT_ENCRYPTION_KEY', '')
    if custom:
        # Expect a Fernet key (44-char urlsafe base64) — use as-is if valid.
        try:
            Fernet(custom.encode() if isinstance(custom, str) else custom)
            return custom.encode() if isinstance(custom, str) else custom
        except Exception:
            pass
        # Otherwise treat as raw string and hash it.
        raw = custom.encode('utf-8')
    else:
        raw = settings.SECRET_KEY.encode('utf-8')
    digest = hashlib.sha256(raw).digest()  # 32 bytes
    return base64.urlsafe_b64encode(digest)


def _fernet() -> Fernet:
    return Fernet(_derive_fernet_key())


def encrypt_value(plaintext: str) -> str:
    if not plaintext:
        return ''
    token = _fernet().encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_value(token: str) -> str:
    if not token:
        return ''
    try:
        return _fernet().decrypt(token.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        # Fallback: value was stored plaintext before encryption was added
        return token


def mask_key(value: str, visible: int = 4) -> str:
    """Mask a key for display: SB-Mid-server-****abcd"""
    if not value:
        return ''
    if len(value) <= visible + 4:
        return '*' * len(value)
    return value[:4] + '*' * (len(value) - visible - 4) + value[-visible:]
