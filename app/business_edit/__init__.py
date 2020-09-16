# coding=utf-8

from flask import Blueprint

business_edit = Blueprint('business_edit', __name__)

from . import views