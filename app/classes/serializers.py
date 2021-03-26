from app import db, ma
from app.classes.btc import *
from app.classes.bch import *
from app.classes.monero import *
from app.classes.business import *
from app.classes.ltc import *
from app.classes.message import *
from app.classes.models import *
from app.classes.notification import *
from app.classes.post import *
from app.classes.report import *
from app.classes.subforum import *
from app.classes.user import *



class BtcPricesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BtcPrices



class XMRPricesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MoneroPrices


class SavedPostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SavedPost

        id = ma.auto_field()
        user_id = ma.auto_field()
        created = ma.auto_field()
        post_id = ma.auto_field()


class PostsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CommonsPost


class SubForumsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SubForums
