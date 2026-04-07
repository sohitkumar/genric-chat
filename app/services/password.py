import bcrypt


def hash_password(password: str) -> str:
    """Return a bcrypt hash string safe to store in password_hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password_hash(password: str, password_hash: str) -> bool:
    """True if password matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        # Malformed hash (e.g. old plaintext in DB)
        return False
