from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Every database model in this project will inherit
    from this class. SQLAlchemy uses this Base to keep
    track of our database tables and their metadata.
    """

    pass