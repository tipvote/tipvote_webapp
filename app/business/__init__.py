# coding=utf-8

from flask import Blueprint

business = Blueprint('business', __name__)

from . import views