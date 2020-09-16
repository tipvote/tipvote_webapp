from app import db
from app.models import BchPrices
from app.common.functions import floating_decimals
from decimal import Decimal


def btc_cash_converttolocal(amount, currency):
    getcurrentprice = db.session.query(BchPrices) \
        .filter_by(currency_id=currency).first()

    bt = getcurrentprice.price
    z = Decimal(bt) * Decimal(amount)
    c = floating_decimals(z, 2)
    return c


def btc_cash_convertlocaltobtc(amount, currency):
    getcurrentprice = db.session.query(BchPrices) \
        .filter_by(currency_id=currency).first()

    bt = getcurrentprice.price
    z = Decimal(amount) / Decimal(bt)
    c = floating_decimals(z, 8)
    return c

