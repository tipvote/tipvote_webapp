from app import db
from app.models import BchWallet
from decimal import Decimal


def checkbalance(user_id, amount):
    # The money requested during the trade
    userwallet = db.session.query(BchWallet).filter_by(user_id=user_id).first()
    x = userwallet.currentbalance
    y = Decimal(amount)

    if x >= y:
        return 1
    else:
        return 0
