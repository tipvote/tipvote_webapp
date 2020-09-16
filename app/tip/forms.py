
from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField
from wtforms.validators import\
    Optional


class CreateTipBTC(FlaskForm):
    """
    Creates a btc tip for a comment
    """

    cent = SubmitField()
    quarter = SubmitField()
    dollar = SubmitField()
    five_dollar = SubmitField()
    ten_dollar = SubmitField()
    twentyfive_dollar = SubmitField()
    hundred_dollar = SubmitField()
    custom_amount = StringField(validators=[
        Optional(),

    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self,*args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class CreateTipBCH(FlaskForm):
    """
    Creates a bch tip for a comment
    """

    cent = SubmitField()
    quarter = SubmitField()
    dollar = SubmitField()
    five_dollar = SubmitField()
    ten_dollar = SubmitField()
    twentyfive_dollar = SubmitField()
    hundred_dollar = SubmitField()
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


class CreateTipXMR(FlaskForm):
    """
    Creates a xmr tip for a comment
    """

    cent = SubmitField()
    quarter = SubmitField()
    dollar = SubmitField()
    five_dollar = SubmitField()
    ten_dollar = SubmitField()
    twentyfive_dollar = SubmitField()
    hundred_dollar = SubmitField()
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


