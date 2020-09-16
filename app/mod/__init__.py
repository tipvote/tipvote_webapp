# coding=utf-8

from flask import Blueprint

mod = Blueprint('mod', __name__)

from . import views