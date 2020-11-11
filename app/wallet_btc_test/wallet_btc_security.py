from decimal import Decimal
from app import db
from app.classes.btc import BtcWalletTest


def checkbalance(user_id, amount):
    # The money requested during the trade
    userwallet = db.session.query(BtcWalletTest).filter_by(user_id=user_id).first()
    x = userwallet.currentbalance
    y = Decimal(amount)

    if x >= y:
        return 1
    else:
        return 0
