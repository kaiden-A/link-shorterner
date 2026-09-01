"""make clicks fk deferrable and cascading

Revision ID: 2bab91676e14
Revises: 865ff98ad244
Create Date: 2026-09-01 11:50:00.816959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bab91676e14'
down_revision: Union[str, Sequence[str], None] = '865ff98ad244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("clicks_link_slug_fkey", "clicks", type_="foreignkey")
    op.create_foreign_key(
        "clicks_link_slug_fkey",
        "clicks",
        "links",
        ["link_slug"],
        ["slug"],
        ondelete="CASCADE",
        deferrable=True,
        initially="DEFERRED",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("clicks_link_slug_fkey", "clicks", type_="foreignkey")
    op.create_foreign_key(
        "clicks_link_slug_fkey",
        "clicks",
        "links",
        ["link_slug"],
        ["slug"],
    )
