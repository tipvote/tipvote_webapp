from app import app
from decimal import Decimal


@app.template_filter('xmrtousd')
def xmrtousd(coinamount):
    """
    Puts the price in currency to btc
    :param price:
    :param currency:
    :return:
    """
    from app.models import MoneroPrices
    from app import db

    getcurrentprice = db.session.query(MoneroPrices).get(1)

    bt = (Decimal(getcurrentprice.price) * coinamount)
    formatteddollar = '{0:.2f}'.format(bt)
    return formatteddollar


@app.template_filter('xmrtocurrency')
def xmrtocurrency(price, currency):
    """
    Puts the price in xmr to currency
    :param price:
    :param currency:
    :return:
    """
    from app.models import MoneroPrices
    from app import db

    getcurrentprice = db.session.query(MoneroPrices) \
        .filter_by(id=currency).first()
    if currency == 1:

        return price
    else:
        x = Decimal(price) / Decimal(getcurrentprice.price)
        bt = (Decimal(getcurrentprice.price) * x)
        c = '{0:.2f}'.format(bt)
        return c


@app.template_filter('xmrprice')
def xmrprice(price, currency):
    """
    gets the price in xmr from a currency and price
    :param price:
    :param currency:
    :return:
    """
    from app.models import MoneroPrices
    from app import db
    getcurrentprice = db.session.query(MoneroPrices) \
        .filter_by(id=currency).first()
    bt = getcurrentprice.price
    z = Decimal(price) / Decimal(bt)
    c = '{0:.8f}'.format(z)
    return c


@app.template_filter('formatxmrtostring')
def formatxmrtostring(value):

    def num_after_point(x):
        s = str(x)
        if not '.' in s:
            return 0
        return len(s) - s.index('.') - 1

    num = num_after_point(value)
    if num > 6:
        c = ('%.08f' % (Decimal(value)))
    else:
        c = value
    return c


@app.template_filter('xmrtostring')
def xmrtostring(value):
    return '%.12f' % value
