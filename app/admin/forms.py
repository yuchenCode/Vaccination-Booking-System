from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


# Form for setting request limit
class RequestLimitForm(FlaskForm):
    request_limit = IntegerField('Patient Request Limit', validators=[DataRequired()])
    submit = SubmitField('Modify')
