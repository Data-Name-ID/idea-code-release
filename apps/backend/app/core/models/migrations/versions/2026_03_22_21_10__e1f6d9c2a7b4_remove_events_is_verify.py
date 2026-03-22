# remove events.is_verify column

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e1f6d9c2a7b4"
down_revision: str | None = "c4b8d2a1e9f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("events", "is_verify")


def downgrade() -> None:
    op.add_column(
        "events",
        sa.Column("is_verify", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("events", "is_verify", server_default=None)
