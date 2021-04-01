# coding=utf-8

from flask import Blueprint

challenge = Blueprint('challenge', __name__)

from . import views