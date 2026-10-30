
"""replace request category text with category foreign key

Revision ID: 25073e9ca220
Revises: c8efd60438f9
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "25073e9ca220"
down_revision: Union[str, Sequence[str], None] = "c8efd60438f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear la columna inicialmente nullable
    op.add_column(
        "requests",
        sa.Column("category_id", sa.Uuid(), nullable=True),
    )

    # 2. Crear índice
    op.create_index(
        "ix_requests_category_id",
        "requests",
        ["category_id"],
        unique=False,
    )

    # 3. Crear clave foránea
    op.create_foreign_key(
        "fk_requests_category_id_categories",
        "requests",
        "categories",
        ["category_id"],
        ["id"],
    )

    # 4. Hacer obligatoria la categoría
    op.alter_column(
        "requests",
        "category_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    # 5. Eliminar la columna antigua
    op.drop_column("requests", "categoria")


def downgrade() -> None:
    # 1. Recuperar la columna anterior
    op.add_column(
        "requests",
        sa.Column("categoria", sa.String(length=50), nullable=True),
    )

    # 2. Recuperar los nombres desde el catálogo
    op.execute("""
        UPDATE requests
        SET categoria = categories.name
        FROM categories
        WHERE requests.category_id = categories.id
    """)

    # 3. Restaurar NOT NULL
    op.alter_column(
        "requests",
        "categoria",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    # 4. Eliminar relación e índice
    op.drop_constraint(
        "fk_requests_category_id_categories",
        "requests",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_requests_category_id",
        table_name="requests",
    )

    # 5. Eliminar columna nueva
    op.drop_column("requests", "category_id")
