# coding=utf-8

from flask import Blueprint

people = Blueprint('people', __name__)

from . import views