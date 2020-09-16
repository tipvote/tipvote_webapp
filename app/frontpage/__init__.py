# coding=utf-8

from flask import Blueprint

frontpage = Blueprint('frontpage', __name__)

from . import views