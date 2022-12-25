from datetime import datetime

from . import login_manager
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


# user DB
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    user_type = db.Column(db.String(16), unique=False, index=True)
    last_seen = db.Column(db.DateTime)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def new_messages(self):
        last_read_time = self.last_seen or datetime(1900, 1, 1, 0, 0, 0)
        return Message.query.filter_by(receiver_email=self.email).filter(Message.time > last_read_time).count()


# patient DB
class Patient(User):
    patient_email = db.Column(db.String(64), unique=True, index=True)
    fullname = db.Column(db.String(16), unique=False, index=True, nullable=True)
    gender = db.Column(db.String(16), unique=False, index=True, nullable=True)
    age = db.Column(db.String(16), unique=False, index=True, nullable=True)
    phone_number = db.Column(db.String(32), unique=True, index=True, nullable=True)
    id_number = db.Column(db.String(32), unique=True, index=True, nullable=True)
    booking = db.Column(db.Integer, unique=False, index=True, nullable=True)
    appointment_id = db.Column(db.Integer, unique=False, index=True, nullable=True)
    vaccination = db.Column(db.Integer, unique=False, index=True, nullable=True)


# doctor DB
class Doctor(User):
    doctor_email = db.Column(db.String(64), unique=True, index=True)
    clinic_id = db.Column(db.String(32), unique=True, index=True, nullable=True)
    clinic_name = db.Column(db.String(16), unique=False, index=True, nullable=True)
    address = db.Column(db.String(64), unique=True, index=True, nullable=True)
    clinic_phone_number = db.Column(db.String(32), unique=True, index=True, nullable=True)


# administrator DB
class Admin(User):
    admin_email = db.Column(db.String(64), unique=True, index=True)
    admin_name = db.Column(db.String(16), unique=False, index=True, nullable=True)
    admin_phone_number = db.Column(db.String(32), unique=True, index=True, nullable=True)
    admin_id = db.Column(db.String(32), unique=True, index=True, nullable=True)
    request_limit = db.Column(db.Integer, unique=False, index=True, nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# vaccination period DB
class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    doctor_email = db.Column(db.String(64), unique=False, index=True)
    clinic_name = db.Column(db.String(16), unique=False, index=True, nullable=True)
    vaccine_type = db.Column(db.String(16), unique=False, index=True, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    time_from = db.Column(db.DateTime, nullable=False)
    time_to = db.Column(db.DateTime, nullable=False)
    limit = db.Column(db.Integer, unique=False, index=True, nullable=True)
    current_booking = db.Column(db.Integer, unique=False, index=True, nullable=True)


# vaccination booking record DB
class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, unique=False, index=True)
    patient_email = db.Column(db.String(64), unique=False, index=True)
    doctor_email = db.Column(db.String(64), unique=False, index=True)
    clinic_name = db.Column(db.String(16), unique=False, index=True, nullable=True)
    vaccine_type = db.Column(db.String(16), unique=False, index=True, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    time_from = db.Column(db.DateTime, nullable=False)
    time_to = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(16), unique=False, index=True)


# message DB
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(64), unique=False, index=True)
    receiver_email = db.Column(db.String(64), unique=False, index=True)
    fullname = db.Column(db.String(16), unique=False, index=True, nullable=True)
    clinic_name = db.Column(db.String(16), unique=False, index=True, nullable=True)
    content = db.Column(db.String(64), unique=False, index=True)
    time = db.Column(db.DateTime, default=datetime.now)
