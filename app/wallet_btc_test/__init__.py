# coding=utf-8

from flask import Blueprint

wallet_btc_test = Blueprint('wallet_btc_test', __name__)

from . import views