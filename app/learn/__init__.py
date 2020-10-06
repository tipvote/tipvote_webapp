
# coding=utf-8

from flask import Blueprint

learn = Blueprint('learn', __name__)

from . import views