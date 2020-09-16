# coding=utf-8

from flask import Blueprint

users = Blueprint('users', __name__)

from . import views