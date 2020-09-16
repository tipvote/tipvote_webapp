# coding=utf-8

from flask import Blueprint

photos = Blueprint('photos', __name__)

from . import views