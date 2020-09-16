
from app.common import common
from app import UPLOADED_FILES_DEST

from flask import send_from_directory, url_for, redirect
from datetime import datetime


now = datetime.utcnow()


@common.route('/<path:filename>')
def media_file(filename):
    try:
        return send_from_directory(UPLOADED_FILES_DEST, filename, as_attachment=False)
    except:
        return url_for('static', filename='images/nobanner.png')


@common.route('/post/image/<path:filename>')
def post_file(filename):
    try:
        return send_from_directory(UPLOADED_FILES_DEST, filename, as_attachment=False)
    except:

        return url_for('static', filename='images/logo.png')


@common.route('/user/image/<path:filename>')
def profile_image(filename):
    try:
        return send_from_directory(UPLOADED_FILES_DEST, filename, as_attachment=False)
    except:

        return url_for('static', filename='images/noprofile.png')


@common.route('/user/banner/image/<path:filename>')
def user_banner_image(filename):
    try:
        return send_from_directory(UPLOADED_FILES_DEST, filename, as_attachment=False)
    except:

            return url_for('static', filename='images/nobanner.png')


@common.route('/subforum/image/banner/<path:filename>')
def banner_image(filename):
    try:
        return send_from_directory(UPLOADED_FILES_DEST, filename, as_attachment=False)
    except:

        return url_for('static', filename='images/nobanner.png')


@common.route('/business/image/<path:filename>')
def business_image(filename):
    try:
        return send_from_directory(UPLOADED_FILES_DEST, filename, as_attachment=False)
    except:

        return url_for('static', filename='images/no-image-icon.png')

