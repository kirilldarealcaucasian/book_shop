"""Remove unique constraint from Product (category_id)

Revision ID: 7b40c3cd150a
Revises: 7dc902eaec0f
Create Date: 2024-02-10 18:53:57.642582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b40c3cd150a'
down_revision: Union[str, None] = '7dc902eaec0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('products_category_id_key', 'products', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('products_category_id_key', 'products', ['category_id'])
    # ### end Alembic commands ###
