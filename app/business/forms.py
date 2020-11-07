from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, \
    FileField

class SubscribeForm(FlaskForm):
    """
    The subscribe button on the side
    """
    subscribe = SubmitField("Subscribe")
    unsubscribe = SubmitField("Unsubscribe")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
