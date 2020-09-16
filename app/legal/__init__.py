
# coding=utf-8

from flask import Blueprint

legal = Blueprint('legal', __name__)

from . import views