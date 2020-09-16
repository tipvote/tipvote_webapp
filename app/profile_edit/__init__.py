# coding=utf-8

from flask import Blueprint

profileedit = Blueprint('profileedit', __name__)

from . import views