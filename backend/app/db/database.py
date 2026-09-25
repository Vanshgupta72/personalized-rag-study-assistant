from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings


# Database engine manages the connection between our application and PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)


# SessionLocal creates database sessions for individual operations.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# FastAPI dependency for getting a database session.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()