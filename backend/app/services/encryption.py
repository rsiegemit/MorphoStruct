"""Encryption service for storing API keys securely."""
import os
import sys
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Encryption key from environment or generate deterministic one from secret
ENV = os.getenv("ENV", "development")
ENCRYPTION_SECRET = os.getenv("ENCRYPTION_SECRET", "shed-encryption-secret-change-in-production")

# Validate secrets on module load
_DEFAULT_SECRET = "shed-encryption-secret-change-in-production"
if ENV != "development" and ENCRYPTION_SECRET == _DEFAULT_SECRET:
    print("ERROR: ENCRYPTION_SECRET is not set or using default value in production!", file=sys.stderr)
    print("Set ENCRYPTION_SECRET environment variable to a secure random value.", file=sys.stderr)
    sys.exit(1)

if ENV == "development" and ENCRYPTION_SECRET == _DEFAULT_SECRET:
    print("WARNING: Using insecure default ENCRYPTION_SECRET in development mode.", file=sys.stderr)
    print("Set ENCRYPTION_SECRET environment variable for production deployment.", file=sys.stderr)

# Cache for storing per-key salts (in production, this should be persisted in DB)
_salt_cache = {}

def _get_fernet(key_id: str = "default") -> Fernet:
    """Get Fernet instance with derived key using unique salt per key_id."""
    # Generate or retrieve salt for this key_id
    if key_id not in _salt_cache:
        # In production, salts should be persisted to database
        # For now, generate random salt that persists in memory
        _salt_cache[key_id] = secrets.token_bytes(16)

    salt = _salt_cache[key_id]

    # Derive a key from the secret using PBKDF2 with unique salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_SECRET.encode()))
    return Fernet(key)

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage."""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage."""
    fernet = _get_fernet()
    decrypted = fernet.decrypt(encrypted_key.encode())
    return decrypted.decode()
