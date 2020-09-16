# coding=utf-8

from flask import Blueprint

wallet_btc = Blueprint('wallet_btc', __name__)

from . import views