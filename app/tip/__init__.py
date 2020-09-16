# coding=utf-8

from flask import Blueprint

tip = Blueprint('tip', __name__)

from . import views