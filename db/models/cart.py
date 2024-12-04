import sqlalchemy as sa

from db.models import Base
from db.models.user import User
from db.models.product import Product


class Cart(Base):
    __tablename__ = "cart"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    product_id = sa.Column(
        sa.ForeignKey(Product.id, ondelete="CASCADE"), nullable=False
    )
    product_name = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Integer, nullable=False)
    cost = sa.Column(sa.Float, nullable=False)
    address = sa.Column(sa.String, nullable=True)
    is_being_delivered = sa.Column(sa.Boolean, server_default="False")
