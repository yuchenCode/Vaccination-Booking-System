import datetime
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from . import doctor
from .. import db
from ..models import Patient, Doctor, Appointment, Record, Message
from .forms import ClinicInfoEditForm, AppointmentCreationForm, MessageForm


# view function for showing clinic profile
@doctor.route('/clinic_info')
@login_required
def clinic_info():
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    return render_template('doctor/clinic_info.html', doctor=doctor)


# view function for editing clinic profile
@doctor.route('/edit_clinic_info', methods=['GET', 'POST'])
@login_required
def edit_clinic_info():
    form = ClinicInfoEditForm()
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    if form.validate_on_submit():
        doctor.clinic_id = form.clinic_id.data
        doctor.clinic_name = form.clinic_name.data
        doctor.address = form.address.data
        try:
            db.session.commit()
        except:
            flash("Invalid address")
            return render_template('doctor/edit_clinic_info.html', form=form)
        doctor.clinic_phone_number = form.clinic_phone_number.data
        try:
            db.session.commit()
        except:
            flash("Invalid phone number")
            return render_template('doctor/edit_clinic_info.html', form=form)
        return redirect(url_for('doctor.clinic_info'))
    elif request.method == 'GET':
        form.clinic_id.data = doctor.clinic_id
        form.clinic_name.data = doctor.clinic_name
        form.address.data = doctor.address
        form.clinic_phone_number.data = doctor.clinic_phone_number
    return render_template('doctor/edit_clinic_info.html', form=form)


# view function for creating vaccination period
@doctor.route('/appointment/create', methods=['get', 'post'])
@login_required
def appointment_create():
    form = AppointmentCreationForm()
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    if form.validate_on_submit():
        appointment = Appointment()
        appointment.doctor_email = doctor.doctor_email
        appointment.clinic_name = doctor.clinic_name
        appointment.vaccine_type = form.vaccination_type.data
        appointment.date = form.date.data
        appointment.time_from = form.time_from.data
        appointment.time_to = form.time_to.data
        appointment.limit = form.limit.data
        appointment.current_booking = 0
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for('doctor.appointment_list'))
    return render_template('doctor/appointment_create.html', form=form, title='Create An Appointment')


# view function for showing vaccination period of current clinic
@doctor.route('/doctor/appointment_list', methods=['get'])
@login_required
def appointment_list():
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    als = Appointment.query.filter_by(doctor_email=current_user.email).all()
    return render_template('doctor/clinic.html', doctor=doctor, als=als)


# view function for viewing patients of one vaccination period
@doctor.route('/doctor/appointment_view_list/<int:appointment_id>')
@login_required
def appointment_view_list(appointment_id):
    rls = Record.query.filter_by(appointment_id=appointment_id).all()
    cls = []
    for r in rls:
        patient = Patient.query.filter_by(patient_email=r.patient_email).first()
        cls.append([patient, r])
    return render_template('doctor/appointment_view.html', cls=cls, appointment_id=appointment_id)


# view function for approving a booking request
@doctor.route('/doctor/appointment_approve/<int:record_id>')
@login_required
def appointment_approve(record_id):
    record = Record.query.filter_by(id=record_id).first()
    record.status = "Approved"
    patient = Patient.query.filter_by(patient_email=record.patient_email).first()
    patient.booking = 1
    patient.vaccination = 1
    doctor = Doctor.query.filter_by(doctor_email=record.doctor_email).first()
    db.session.query(Record).filter(Record.patient_email == patient.patient_email).\
        filter(Record.status != "Approved").delete()
    db.session.commit()

    message = Message()
    message.sender_email = current_user.email
    message.receiver_email = patient.patient_email
    message.clinic_name = doctor.clinic_name
    message.content = "The time period you booked (" + record.date.strftime("%m-%d") + " " + \
                      record.time_from.strftime("%H:%M") + " to " + record.time_to.strftime("%H:%M") + ") in " +\
                      record.clinic_name + " clinic has been Approved"
    message.time = datetime.datetime.now()
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('doctor.appointment_view_list', appointment_id=record.appointment_id))


# view function for rejecting a booking request
@doctor.route('/doctor/appointment_reject/<int:record_id>')
@login_required
def appointment_reject(record_id):
    record = Record.query.filter_by(id=record_id).first()
    record.status = "Rejected"
    patient = Patient.query.filter_by(patient_email=record.patient_email).first()
    patient.booking -= 1
    doctor = Doctor.query.filter_by(doctor_email=record.doctor_email).first()
    appointment = Appointment.query.filter_by(id=record.appointment_id).first()
    appointment.current_booking -= 1
    db.session.commit()

    message = Message()
    message.sender_email = current_user.email
    message.receiver_email = patient.patient_email
    message.clinic_name = doctor.clinic_name
    message.content = "The time period you booked (" + record.date.strftime("%m-%d") + " " + \
                      record.time_from.strftime("%H:%M") + " to " + record.time_to.strftime("%H:%M") + ") in " +\
                      record.clinic_name + " clinic has been rejected"
    message.time = datetime.datetime.now()
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('doctor.appointment_view_list', appointment_id=record.appointment_id))


# view function for deleting a vaccination period
@doctor.route('/appointment/delete/<int:appointment_id>')
@login_required
def appointment_delete(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    db.session.delete(appointment)
    count = db.session.query(Record).filter(Record.appointment_id == appointment_id).count()
    db.session.query(Record).filter(Record.appointment_id == appointment_id).delete()
    db.session.commit()
    patient = Patient.query.filter_by(appointment_id=appointment_id).all()
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    for p in patient:
        db.session.query(Record).filter(Record.appointment_id == appointment_id).\
            filter(Record.patient_email == p.patient_email).delete()
        p.booking -= count
        p.vaccination = 0
        db.session.commit()
        message = Message()
        message.sender_email = current_user.email
        message.receiver_email = p.patient_email
        message.clinic_name = doctor.clinic_name
        message.content = "Sorry, the time period you booked (" + appointment.time_from.strftime("%m-%d %H:%M") +\
                          " to " + appointment.time_to.strftime("%m-%d %H:%M") + ") is canceled"
        message.time = datetime.datetime.now()
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('doctor.appointment_list'))


# view function for accomplishing vaccination
@doctor.route('/doctor/accomplish_vaccination/<record_id>')
@login_required
def accomplish_vaccination(record_id):
    record = Record.query.filter_by(id=record_id).first()
    patient = Patient.query.filter_by(patient_email=record.patient_email).first()
    patient.vaccination = 2
    db.session.commit()
    return redirect(url_for('doctor.appointment_view_list', appointment_id=record.appointment_id))


# view function for contacting patients
@doctor.route('/doctor/contact/<appointment_id>/<patient_email>', methods=['get', 'POST'])
@login_required
def contact(patient_email, appointment_id):
    form = MessageForm()
    patient = Patient.query.filter_by(patient_email=patient_email).first()
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    if form.validate_on_submit():
        message = Message()
        message.sender_email = current_user.email
        message.receiver_email = patient_email
        message.fullname = patient.fullname
        message.clinic_name = doctor.clinic_name
        message.content = form.message.data
        message.time = datetime.datetime.now()
        db.session.add(message)
        db.session.commit()
        flash("Message sent")
        return redirect(url_for('doctor.appointment_view_list', appointment_id=appointment_id))
    return render_template('doctor/contact.html', form=form)


# view function for replying patients
@doctor.route('/doctor/reply/<fullname>', methods=['get', 'POST'])
@login_required
def reply(fullname):
    form = MessageForm()
    patient = Patient.query.filter_by(fullname=fullname).first()
    doctor = Doctor.query.filter_by(doctor_email=current_user.email).first()
    if form.validate_on_submit():
        message = Message()
        message.sender_email = current_user.email
        message.receiver_email = patient.patient_email
        message.fullname = fullname
        message.clinic_name = doctor.clinic_name
        message.content = form.message.data
        message.time = datetime.datetime.now()
        db.session.add(message)
        db.session.commit()
        flash("Message sent")
        return redirect(url_for('doctor.message'))
    return render_template('doctor/reply.html', form=form)


# view function for showing messages
@doctor.route('/doctor/message', methods=['get'])
@login_required
def message():
    message = Message.query.filter_by(receiver_email=current_user.email).all()
    mls = message[::-1]
    return render_template('doctor/message.html', mls=mls)
