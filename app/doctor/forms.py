from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.validators import ValidationError


# Form for edit clinic profile
class ClinicInfoEditForm(FlaskForm):
    clinic_id = StringField('Clinic ID', validators=[DataRequired(), Length(1, 32), Regexp('[0-9]')])
    clinic_name = StringField('Clinic Name', validators=[DataRequired(), Length(1, 16), Regexp('[A-Za-z]')])
    address = StringField('Address', validators=[DataRequired(), Length(1, 64)])
    clinic_phone_number = StringField('Phone Number', validators=[DataRequired(), Length(1, 32), Regexp('[0-9]')])
    submit = SubmitField('Submit')


# Form for create vaccination period
class AppointmentCreationForm(FlaskForm):
    vaccination_type = SelectField('Vaccination Type', validators=[DataRequired()], choices=[('Sinovac', 'Sinovac'),
                                                                                             ('CanSino', 'CanSino'),
                                                                                             ('Pfizer', 'Pfizer'),
                                                                                             ('Moderna', 'Moderna')])
    date = DateTimeField('Appointment Date', validators=[DataRequired()], format='%Y-%m-%d')
    time_from = DateTimeField('Appointment Time Start', validators=[DataRequired()], format='%H:%M')
    time_to = DateTimeField('Appointment Time End', validators=[DataRequired()], format='%H:%M')
    limit = IntegerField('Booking Limit', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # verify the time chose
    def validate_time_to(self, time_to):
        time_to = time_to.data
        time_form = self.time_from.data
        if time_to < time_form:
            raise ValidationError('Appointment time end should be lager than start')


# Form for sending messages
class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Send')
