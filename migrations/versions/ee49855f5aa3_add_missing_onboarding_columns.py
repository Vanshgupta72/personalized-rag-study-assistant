"""add missing onboarding columns"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "ee49855f5aa3"
down_revision: Union[str, Sequence[str], None] = "d4181ab90918"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_preferences",
        sa.Column(
            "learning_profile",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "onboarding_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column(
        "user_preferences",
        "learning_profile",
        server_default=None,
    )
    op.alter_column(
        "user_preferences",
        "onboarding_completed",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("user_preferences", "onboarding_completed")
    op.drop_column("user_preferences", "learning_profile")
