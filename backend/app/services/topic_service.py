from sqlalchemy.orm import Session

from backend.app.models.topic import Topic


def create_topic(
    db: Session,
    subject_id: int,
    name: str
) -> Topic:
    topic = Topic(
        subject_id=subject_id,
        name=name.strip()
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return topic


def get_subject_topics(
    db: Session,
    subject_id: int
) -> list[Topic]:
    return (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.name.asc())
        .all()
    )


def get_topic(
    db: Session,
    topic_id: int,
    subject_id: int
) -> Topic | None:
    return (
        db.query(Topic)
        .filter(
            Topic.id == topic_id,
            Topic.subject_id == subject_id
        )
        .first()
    )


def delete_topic(
    db: Session,
    topic: Topic
) -> None:
    db.delete(topic)
    db.commit()