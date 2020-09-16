from flask import \
    render_template

from app.admin import admin


@admin.route('/home', methods=['GET'])
def home():

    return render_template('coins/bank.html',
                           # forms

                           )