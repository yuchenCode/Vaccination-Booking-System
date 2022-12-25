import datetime
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user

from . import patient
from .. import db
from ..models import Patient, Doctor, Appointment, Record, Message, Admin
from .forms import ProfileEditForm, MessageForm


# view function for showing profile
@patient.route('/profile')
@login_required
def profile():
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    return render_template('patient/profile.html', patient=patient)


# view function for editing profile
@patient.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm()
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    if form.validate_on_submit():
        patient.fullname = form.fullname.data
        patient.gender = form.gender.data
        patient.age = form.age.data
        patient.phone_number = form.phone_number.data
        try:
            db.session.commit()
        except:
            flash("Invalid phone number")
            return render_template('patient/edit_profile.html', form=form)
        patient.id_number = form.id_number.data
        try:
            db.session.commit()
        except:
            flash("Invalid ID number")
            return render_template('patient/edit_profile.html', form=form)
        return redirect(url_for('patient.profile'))
    elif request.method == 'GET':
        form.fullname.data = patient.fullname
        form.gender.data = patient.gender
        form.age.data = patient.age
        form.phone_number.data = patient.phone_number
        form.id_number.data = patient.id_number
    return render_template('patient/edit_profile.html', form=form)


# view function for showing all clinics
@patient.route('/patient/appointment_clinic_list', methods=['GET', 'POST'])
@login_required
def appointment_clinic_list():
    name = request.form.get("clinic")
    cls = Appointment.query.with_entities(Appointment.clinic_name).distinct().all()
    for c in cls:
        if name == c[0]:
            cls = Appointment.query.filter_by(clinic_name=name).with_entities(Appointment.clinic_name).distinct().all()
            break
    return render_template('patient/appointment_clinic.html', cls=cls)


# view function for showing all available vaccination period in one clinic
@patient.route('/patient/appointment_period_list/<clinic_name>', methods=['GET', 'POST'])
@login_required
def appointment_period_list(clinic_name):
    start = request.form.get("start")
    type = request.form.get("type")
    als = db.session.query(Appointment).filter(Appointment.clinic_name == clinic_name).all()
    rls = db.session.query(Record).filter(Record.patient_email == current_user.email).all()
    idlist = []
    for r in rls:
        idlist.append(r.appointment_id)
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    admin = db.session.query(Admin).filter(Admin.request_limit != "").first()
    if type is not None and type != "All" and type is not None:
        als = db.session.query(Appointment).filter(Appointment.clinic_name == clinic_name,
                                                   Appointment.vaccine_type == type).all()
        if start != "":
            start = datetime.datetime.strptime(start, '%H:%M')
            als = db.session.query(Appointment).filter(Appointment.clinic_name == clinic_name,
                                                       Appointment.vaccine_type == type, Appointment.time_from <= start,
                                                       Appointment.time_to >= start).all()
    else:
        als = db.session.query(Appointment).filter(Appointment.clinic_name == clinic_name).all()
        if start != "" and start is not None:
            start = datetime.datetime.strptime(start, '%H:%M')
            als = db.session.query(Appointment).filter(Appointment.clinic_name == clinic_name,
                                                       Appointment.time_from <= start,
                                                       Appointment.time_to >= start).all()
    return render_template('patient/appointment_period.html', als=als, idlist=idlist, patient=patient, admin=admin,
                           clinic_name=clinic_name)


# view function for booking
@patient.route('/patient/booking/<int:appointment_id>')
@login_required
def booking(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    appointment.current_booking += 1
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    patient.booking += 1
    patient.appointment_id = appointment_id

    record = Record()
    record.appointment_id = appointment.id
    record.patient_email = current_user.email
    record.doctor_email = appointment.doctor_email
    record.clinic_name = appointment.clinic_name
    record.vaccine_type = appointment.vaccine_type
    record.date = appointment.date
    record.time_from = appointment.time_from
    record.time_to = appointment.time_to
    record.status = "In Progress"
    db.session.add(record)
    db.session.commit()

    message = Message()
    message.sender_email = current_user.email
    message.receiver_email = appointment.doctor_email
    message.fullname = patient.fullname
    message.content = \
        patient.fullname + " submitted a booking request on " + appointment.date.strftime("%m-%d") + " " + \
        appointment.time_from.strftime("%H:%M") + " to " + appointment.time_to.strftime("%H:%M")
    message.time = datetime.datetime.now()
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('patient.appointment_period_list', clinic_name=appointment.clinic_name))


# view function for showing booking status
@patient.route('/patient/appointment_status', methods=['get'])
@login_required
def appointment_status():
    rls = Record.query.filter_by(patient_email=current_user.email).all()
    return render_template('patient/appointment_status.html', rls=rls)


# view function for contacting doctors
@patient.route('/patient/contact/<clinic_name>', methods=['get', 'POST'])
@login_required
def contact(clinic_name):
    form = MessageForm()
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    doctor = Doctor.query.filter_by(clinic_name=clinic_name).first()
    if form.validate_on_submit():
        message = Message()
        message.sender_email = current_user.email
        message.receiver_email = doctor.doctor_email
        message.fullname = patient.fullname
        message.clinic_name = clinic_name
        message.content = form.message.data
        message.time = datetime.datetime.now()
        db.session.add(message)
        db.session.commit()
        flash("Message sent")
        return redirect(url_for('patient.appointment_clinic_list'))
    return render_template('patient/contact.html', form=form)


# view function for replying doctors
@patient.route('/patient/reply/<clinic_name>', methods=['get', 'POST'])
@login_required
def reply(clinic_name):
    form = MessageForm()
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    doctor = Doctor.query.filter_by(clinic_name=clinic_name).first()
    if form.validate_on_submit():
        message = Message()
        message.sender_email = current_user.email
        message.receiver_email = doctor.doctor_email
        message.fullname = patient.fullname
        message.clinic_name = clinic_name
        message.content = form.message.data
        message.time = datetime.datetime.now()
        db.session.add(message)
        db.session.commit()
        flash("Message sent")
        return redirect(url_for('patient.message'))
    return render_template('patient/reply.html', form=form)


# view function for showing messages
@patient.route('/patient/message', methods=['get'])
@login_required
def message():
    message = Message.query.filter_by(receiver_email=current_user.email).all()
    mls = message[::-1]
    return render_template('patient/message.html', mls=mls)


# view function for showing map
@patient.route('/patient/direct')
@login_required
def direct():
    return render_template('patient/direct.html')


@patient.route('/patient/form')
@login_required
def form():
    patient = Patient.query.filter_by(patient_email=current_user.email).first()
    record = Record.query.filter_by(patient_email=patient.patient_email).first()
    clinic = Doctor.query.filter_by(doctor_email=record.doctor_email).first()
    return render_template('patient/form.html', patient=patient, record=record,
                           clinic=clinic)
