# Import the User model so it is available
# through the models package.
from backend.app.models.user import User


# Define the public objects exposed by this package.
__all__ = ["User"]