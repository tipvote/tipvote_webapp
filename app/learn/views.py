from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, \
    request

from app.learn import learn


@learn.route('/home', methods=['GET'])
def main():
    if request.method == 'GET':

        return render_template('learn/main.html')

    if request.method == 'POST':
        pass


# BITCOIN

@learn.route('/learn/btc', methods=['GET'])
def learn_btc():
    if request.method == 'GET':

        return render_template('learn/btc/main.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/btc/basics', methods=['GET'])
def learn_btc_basics():
    if request.method == 'GET':
        return render_template('learn/btc/basics.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/btc/wallets', methods=['GET'])
def learn_btc_wallets():
    if request.method == 'GET':
        return render_template('learn/btc/wallets.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/btc/gettingbtc', methods=['GET'])
def learn_btc_getting():
    if request.method == 'GET':
        return render_template('learn/btc/getting.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/btc/spending', methods=['GET'])
def learn_btc_spending():
    if request.method == 'GET':
        return render_template('learn/btc/spending.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/btc/selling', methods=['GET'])
def learn_btc_selling():
    if request.method == 'GET':
        return render_template('learn/btc/selling.html')

    if request.method == 'POST':
        pass




# BITCOIN CASH

@learn.route('/learn/bch', methods=['GET'])
def learn_bch():
    if request.method == 'GET':

        return render_template('learn/bch/main.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/bch/basics', methods=['GET'])
def learn_bch_basics():
    if request.method == 'GET':
        return render_template('learn/bch/basics.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/bch/wallets', methods=['GET'])
def learn_bch_wallets():
    if request.method == 'GET':
        return render_template('learn/bch/wallets.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/bch/gettingbch', methods=['GET'])
def learn_bch_getting():
    if request.method == 'GET':
        return render_template('learn/bch/getting.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/bch/spending', methods=['GET'])
def learn_bch_spending():
    if request.method == 'GET':
        return render_template('learn/bch/spending.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/bch/selling', methods=['GET'])
def learn_bch_selling():
    if request.method == 'GET':
        return render_template('learn/bch/selling.html')

    if request.method == 'POST':
        pass


# MONERO

@learn.route('/learn/xmr', methods=['GET'])
def learn_xmr():
    if request.method == 'GET':

        return render_template('learn/xmr/main.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/xmr/basics', methods=['GET'])
def learn_xmr_basics():
    if request.method == 'GET':
        return render_template('learn/xmr/basics.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/xmr/wallets', methods=['GET'])
def learn_xmr_wallets():
    if request.method == 'GET':
        return render_template('learn/xmr/wallets.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/xmr/gettingbch', methods=['GET'])
def learn_xmr_getting():
    if request.method == 'GET':
        return render_template('learn/xmr/getting.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/xmr/spending', methods=['GET'])
def learn_xmr_spending():
    if request.method == 'GET':
        return render_template('learn/xmr/spending.html')

    if request.method == 'POST':
        pass


@learn.route('/learn/xmr/selling', methods=['GET'])
def learn_xmr_selling():
    if request.method == 'GET':
        return render_template('learn/xmr/selling.html')

    if request.method == 'POST':
        pass
