import sqlalchemy as sa

from db.models import Base


class User(Base):
    __tablename__ = "admin_panel_user"

    id = sa.Column(sa.BigInteger, primary_key=True)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=True)
    username = sa.Column(sa.String, nullable=True)
    lang = sa.Column(sa.String, server_default="en")
