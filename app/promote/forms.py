from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp, Optional
from app.common.validation import subcommon_name, \
    onlynumbers, \
    general, bitcoin


class CreatePromotePostBtc(FlaskForm):
    """
    Creates a btc tip for a comment
    """
    cent_btc = SubmitField()
    quarter_btc = SubmitField()
    dollar_btc = SubmitField()
    five_dollar_btc = SubmitField()
    ten_dollar_btc = SubmitField()
    twentyfive_dollar_btc = SubmitField()
    hundred_dollar_btc = SubmitField()

    custom_amount = StringField(validators=[
        Optional(),

    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class CreatePromotePostBch(FlaskForm):
    """
    Creates a btc tip for a comment
    """
    cent_bch = SubmitField()
    quarter_bch = SubmitField()
    dollar_bch = SubmitField()
    five_dollar_bch = SubmitField()
    ten_dollar_bch = SubmitField()
    twentyfive_dollar_bch = SubmitField()
    hundred_dollar_bch = SubmitField()

    custom_amount = StringField(validators=[
        Optional(),

    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class CreatePromotePostXmr(FlaskForm):
    """
    Creates a btc tip for a comment
    """
    cent_xmr = SubmitField()
    quarter_xmr = SubmitField()
    dollar_xmr = SubmitField()
    five_dollar_xmr = SubmitField()
    ten_dollar_xmr = SubmitField()
    twentyfive_dollar_xmr = SubmitField()
    hundred_dollar_xmr = SubmitField()

    custom_amount = StringField(validators=[
        Optional(),

    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True



class GiveCoin(FlaskForm):
    """
    Creates a coin giove to post
    """

    give_coin = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


