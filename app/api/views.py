from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, \
    request,\
    jsonify,\
    make_response

from app import db, app
from app.api import api
from datetime import datetime
from sqlalchemy import or_, func
from flask_cors import CORS, cross_origin

from app.classes.serializers import *

from app.classes.btc import *
from app.classes.bch import *
from app.classes.business import *
from app.classes.ltc import *
from app.classes.message import *
from app.classes.models import *
from app.classes.notification import *
from app.classes.post import *
from app.classes.report import *
from app.classes.subforum import *
from app.classes.user import *


# @api.route('', methods=['GET'])
#
# def index_all():
#     """
#     Gets the index query for landing page
#     :return:
#     """
#
#     posts = db.session.query(CommonsPost)
#     posts = posts.filter(CommonsPost.hidden == 0)
#     posts = posts.order_by(CommonsPost.hotness_rating_now.desc(), CommonsPost.created.desc())
#     posts = posts.limit(20)
#
#     posts_schema = PostsSchema( many=True)
#
#     return jsonify(posts_schema.dump(posts))
#
# @api.route('/new', methods=['GET'])
# @cross_origin()
# def index_new():
#     """
#     Gets the newest posts
#     :return:
#     """
#
#     posts = db.session.query(CommonsPost)
#     posts = posts.filter(CommonsPost.hidden == 0)
#     posts = posts.order_by(CommonsPost.created.desc())
#     posts = posts.limit(200)
#
#     posts_schema = PostsSchema(many=True)
#
#     return jsonify(posts_schema.dump(posts))
#
#
# @api.route('/price/btc', methods=['GET'])
# @cross_origin()
# def btc_price():
#     """
#     Returns the BTC Price
#     :return:
#     """
#
#     price = db.session.query(BtcPrices).first()
#
#     price_schema = BtcPricesSchema()
#
#     return jsonify(price_schema.dump(price))
#
#
# @api.route('/price/bch', methods=['GET'])
# @cross_origin()
# def bch_price():
#     """
#     Returns the BCH Price
#     :return:
#     """
#
#     price = db.session.query(BchPrices).first()
#
#     price_schema = BtcPricesSchema()
#
#     return jsonify(price_schema.dump(price))
#
#
# @api.route('/price/xmr', methods=['GET'])
# @cross_origin()
# def xmr_price():
#     """
#     Returns the XMR Price
#     :return:
#     """
#
#     price = db.session.query(XMRPrices).first()
#
#     price_schema = BtcPricesSchema()
#
#     return jsonify(price_schema.dump(price))
#
#
#
# @api.route('/rooms', methods=['GET'])
# @cross_origin()
# def rooms_all():
#     """
#     Returns all rooms
#     :return:
#     """
#
#     all_rooms = db.session.query(SubForums).order_by(SubForums.created.desc()).all()
#
#     rooms_schema = SubForumsSchema(many=True)
#
#     return jsonify(rooms_schema.dump(all_rooms))
#
#
# @api.route('/rooms/<int:user_id>', methods=['GET'])
# @cross_origin()
# def rooms_user_subscribed(user_id):
#     """
#     Returns rooms user is subscribed too
#     :return:
#     """
#
#     usersubforums = db.session.query(Subscribed)
#     usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
#     usersubforums = usersubforums.filter(user_id == Subscribed.user_id)
#     usersubforums = usersubforums.filter(SubForums.room_banned == 0,
#                                          SubForums.room_deleted == 0,
#                                          SubForums.room_suspended == 0
#                                          )
#     usersubforums = usersubforums.filter(SubForums.id != 1)
#     usersubforums = usersubforums.order_by((SubForums.id == 31).desc(), SubForums.subcommon_name)
#     usersubforums = usersubforums.all()
#
#     user_rooms_schema = SubForumsSchema(many=True)
#
#     return jsonify(user_rooms_schema.dump(usersubforums))
#
#
# @api.route('/rooms/guest', methods=['GET'])
# @cross_origin()
# def rooms_guest(username):
#     """
#     Returns rooms for guests
#     :return:
#     """
#
#     guestsubforums = db.session.query(SubForums)
#     guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
#     guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
#     guestsubforums = guestsubforums.filter(SubForums.room_banned == 0,
#                                            SubForums.room_deleted == 0,
#                                            SubForums.room_suspended == 0,
#                                            )
#     guestsubforums = guestsubforums.filter(SubForums.id != 1, SubForums.id != 13)
#     guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
#     guestsubforums = guestsubforums.limit(7)
#
#     guest_rooms_schema = SubForumsScheme(many=True)
#
#     return jsonify(guest_rooms_schema.dump(guestsubforums))
