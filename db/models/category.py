import sqlalchemy as sa

from db.models import Base


class Category(Base):
    __tablename__ = "category"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
