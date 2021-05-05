from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, \
    FileField

class Form(FlaskForm):
    """
    The subscribe button on the side
    """
    submit = SubmitField("Subscribe")


    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
