import sqlalchemy as sa

from db.models import Base
from db.models.category import Category


class Product(Base):
    __tablename__ = "admin_panel_product"

    id = sa.Column(sa.Integer, primary_key=True)
    category_id = sa.Column(
        sa.ForeignKey(Category.id, ondelete="CASCADE"), nullable=False
    )
    name = sa.Column(sa.String, nullable=False)
    photo = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    amount = sa.Column(sa.Integer, server_default="0")
