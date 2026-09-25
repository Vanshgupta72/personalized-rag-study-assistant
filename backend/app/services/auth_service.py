# pwdlib provides secure password hashing and verification.
# We use Argon2 because it is designed specifically for
# securely storing passwords.
from pwdlib import PasswordHash


# Create one reusable password hasher.
# The default configuration uses a secure password-hashing algorithm.
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure password hash.

    We store the returned hash in PostgreSQL instead of
    storing the user's original password.
    """

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Check whether a plain-text password matches
    the previously stored password hash.

    Returns:
        True  -> password is correct
        False -> password is incorrect
    """

    return password_hasher.verify(password, password_hash)