from backend.app.db.base import Base
from backend.app.db.database import engine

from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.user_preference import UserPreference
from backend.app.models.subject import Subject
from backend.app.models.topic import Topic
from backend.app.models.learning_history import LearningHistory


Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")