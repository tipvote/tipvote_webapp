# coding=utf-8

from flask import Blueprint

ads = Blueprint('ads', __name__)

from . import views