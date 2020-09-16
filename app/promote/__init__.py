# coding=utf-8

from flask import Blueprint

promote = Blueprint('promote', __name__)

from . import views