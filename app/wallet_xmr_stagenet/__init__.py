# coding=utf-8

from flask import Blueprint

wallet_xmr_stagenet = Blueprint('wallet_xmr_stagenet', __name__)

from . import views