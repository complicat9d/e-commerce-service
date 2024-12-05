import sqlalchemy as sa

from db.models import Base


class FAQ(Base):
    __tablename__ = "admin_panel_faq"

    id = sa.Column(sa.BigInteger, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=False)
