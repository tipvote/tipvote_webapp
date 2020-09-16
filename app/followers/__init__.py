# coding=utf-8

from flask import Blueprint

followers = Blueprint('followers', __name__)

from . import views