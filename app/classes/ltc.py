from app import db
from datetime import datetime
import bleach
from markdown import markdown


class LtcPrices(db.Model):
    __tablename__ = 'prices_ltc'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_main", 'useexisting': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.DECIMAL(50, 2))
