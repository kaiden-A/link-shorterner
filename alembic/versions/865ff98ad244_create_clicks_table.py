"""create clicks table

Revision ID: 865ff98ad244
Revises: 1c62b2d4aeb4
Create Date: 2026-07-27 21:11:10.776745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '865ff98ad244'
down_revision: Union[str, Sequence[str], None] = '1c62b2d4aeb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id SERIAL NOT NULL,
            link_slug VARCHAR NOT NULL,
            timestamp TIMESTAMP WITHOUT TIME ZONE,
            referer VARCHAR,
            source VARCHAR,
            utm_source VARCHAR,
            user_agent VARCHAR,
            device_type VARCHAR,
            browser VARCHAR,
            os VARCHAR,
            ip_address VARCHAR,
            PRIMARY KEY (id),
            FOREIGN KEY (link_slug) REFERENCES links (slug)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_clicks_id ON clicks (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_clicks_link_slug ON clicks (link_slug)")


def downgrade() -> None:
    op.drop_index(op.f("ix_clicks_link_slug"), table_name="clicks")
    op.drop_index(op.f("ix_clicks_id"), table_name="clicks")
    op.drop_table("clicks")