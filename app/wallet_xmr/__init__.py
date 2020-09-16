# coding=utf-8

from flask import Blueprint

wallet_xmr = Blueprint('wallet_xmr', __name__)

from . import views