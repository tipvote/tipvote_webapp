from flask import Blueprint

wallet_bch = Blueprint('wallet_bch', __name__)

from . import views