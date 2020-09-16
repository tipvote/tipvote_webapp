# coding=utf-8

from flask import Blueprint

coins = Blueprint('coins', __name__)

from . import views