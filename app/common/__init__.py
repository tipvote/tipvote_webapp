# coding=utf-8

from flask import Blueprint

common = Blueprint('common', __name__)

from . import views