from app import app
from decimal import Decimal


@app.template_filter('btctousd')
def btctousd(coinamount):

    from app.models import BtcPrices
    from app import db

    getcurrentprice = db.session.query(BtcPrices).get(1)

    bt = (Decimal(getcurrentprice.price) * coinamount)
    formatteddollar = '{0:.2f}'.format(bt)
    return formatteddollar


@app.template_filter('btcprice')
def btcprice(price, currency):

    from app.models import BtcPrices
    from app import db
    getcurrentprice = db.session.query(BtcPrices) \
        .filter_by(id=currency).first()
    bt = getcurrentprice.price
    z = Decimal(price) / Decimal(bt)
    c = '{0:.8f}'.format(z)
    return c


@app.template_filter('currencyformat')
def currencyformat(id):

    from app import db
    from app.models import BtcPrices

    getfilter = db.session.query(BtcPrices).filter_by(code=id).first()
    return getfilter.symbol


@app.template_filter('btctostring')
def btctostring(value):
    return '%.08f' % value