from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp


# Form for edit profile
class ProfileEditForm(FlaskForm):
    fullname = StringField('Fullname', validators=[DataRequired(), Length(1, 16), Regexp('[A-Za-z]')])
    gender = SelectField('Gender', validators=[DataRequired()], choices=[('Male', 'Male'), ('Female', 'Female')])
    age = StringField('Age', validators=[DataRequired(), Length(1, 16), Regexp('[0-9]')])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(1, 32), Regexp('[0-9]')])
    id_number = StringField('ID Number', validators=[DataRequired(), Length(1, 32), Regexp('[0-9]')])
    submit = SubmitField('Submit')


# Form for sending messages
class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Send')
