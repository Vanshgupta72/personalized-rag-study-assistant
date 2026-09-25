# Import Base.
# Base keeps track of all SQLAlchemy models.
from backend.app.db.base import Base

# Import the database engine.
# The engine connects our application to PostgreSQL.
from backend.app.db.database import engine

# Import User so SQLAlchemy knows that the
# 'users' table needs to be created.
from backend.app.models.user import User


# create_all() checks the metadata registered with Base
# and creates tables that do not already exist.
#
# It does NOT delete existing tables.
Base.metadata.create_all(bind=engine)


# Simple confirmation message for the terminal.
print("Database tables created successfully.")