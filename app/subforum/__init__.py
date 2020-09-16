# coding=utf-8

from flask import Blueprint

subforum = Blueprint('subforum', __name__)

from . import views
