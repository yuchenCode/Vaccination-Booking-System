import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Patient, Doctor, Admin
from .forms import LoginForm, RegistrationForm


# view function for home page
@auth.route('/')
def index():
    return render_template('auth/index.html')


# view function for login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            current_user.last_seen = datetime.datetime.now()
            db.session.commit()
            if current_user.user_type == "Patient":
                return redirect(url_for('patient.appointment_clinic_list'))
            elif current_user.user_type == "Doctor":
                return redirect(url_for("doctor.appointment_list"))
            elif current_user.user_type == "Administrator":
                return redirect(url_for('admin.admin_patient'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


# view function for register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if db.session.query(User).filter(User.email == form.email.data).count() == 0:
        if form.validate_on_submit():
            user = User(email=form.email.data, password=form.password.data, user_type=form.user_type.data)
            db.session.add(user)
            db.session.commit()
            if form.user_type.data == "Patient":
                patient = Patient(patient_email=form.email.data, booking=0, vaccination=0)
                db.session.add(patient)
                db.session.commit()
            elif form.user_type.data == "Doctor":
                doctor = Doctor(doctor_email=form.email.data)
                db.session.add(doctor)
                db.session.commit()
            elif form.user_type.data == "Administrator":
                admin = Admin(admin_email=form.email.data, request_limit=3)
                db.session.add(admin)
                db.session.commit()
            flash('You can login now.')
            return redirect(url_for('auth.login'))
    else:
        flash("This email is used already.")
    return render_template('auth/register.html', form=form)


# view function for log out
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.index'))


# view function for continuing the work
@auth.route('/continue')
def continue_work():
    if current_user.user_type == "Patient":
        return redirect(url_for('patient.appointment_clinic_list'))
    elif current_user.user_type == "Doctor":
        return redirect(url_for("doctor.appointment_list"))
    elif current_user.user_type == "Administrator":
        return redirect(url_for('admin.admin_patient'))
