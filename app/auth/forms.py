from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email


# Form for login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


# Form for login
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must '
                                                                                                  'match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    user_type = SelectField('Register as:', validators=[DataRequired()], choices=[('Patient', 'Patient'), ('Doctor',
                                                                        'Doctor'), ('Administrator', 'Administrator')])
    submit = SubmitField('Register')

