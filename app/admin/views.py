from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import admin
from .. import db
from ..models import User, Patient, Doctor, Admin, Record, Appointment
from .forms import RequestLimitForm
from pyecharts import options as opts
from pyecharts.charts import Pie


# view function for patient account showing
@admin.route('/admin/appointment/list_patient', methods=['GET', 'POST'])
@login_required
def admin_patient():
    if request.method == 'POST':
        idn = request.form.get('id_number')
        i = request.form.get('id')
        if i is not None:
            patient_aim = db.session.query(Patient).filter(Patient.id == i).first()
            user_aim = db.session.query(User).filter(User.email == patient_aim.patient_email).first()
            db.session.query(Record).filter(Record.patient_email == patient_aim.patient_email).delete()
            db.session.delete(patient_aim)
            db.session.delete(user_aim)
        if i is None:
            if idn == ' ':
                flash("The patient can only be modified when he/she owns an ID Number.")
            else:
                patient_aim = db.session.query(Patient).filter(Patient.id_number == idn).first()
                if request.form.get('fullname') != '':
                    patient_aim.fullname = request.form.get('fullname')
                if request.form.get('gender') != '':
                    patient_aim.gender = request.form.get('gender')
                if request.form.get('email') != '':
                    db.session.query(User).filter(User.email == patient_aim.patient_email).first().email = request.form.get('email')
                    patient_aim.patient_email = request.form.get('email')
                if request.form.get('vaccination') != '':
                    patient_aim.vaccination = request.form.get('vaccination')
        db.session.commit()
    p = db.session.query(Patient).filter(Patient.patient_email != '').order_by(Patient.id).all()
    return render_template('admin/admin_patient.html', patient=p)


# view function for doctor account showing
@admin.route('/admin/appointment/list_doctor', methods=['GET', 'POST'])
@login_required
def admin_doctor():
    if request.method == 'POST':
        cid = request.form.get('clinic_id')
        i = request.form.get('id')
        if i is not None:
            doctor_aim = db.session.query(Doctor).filter(Doctor.id == i).first()
            user_aim = db.session.query(User).filter(User.email == doctor_aim.doctor_email).first()
            record_aim = db.session.query(Record).filter(Record.doctor_email == doctor_aim.doctor_email).all()
            for r in record_aim:
                patient_aim = db.session.query(Patient).filter(Patient.patient_email == r.patient_email).first()
                patient_aim.booking -= 1
            db.session.query(Appointment).filter(Appointment.doctor_email == doctor_aim.doctor_email).delete()
            db.session.query(Record).filter(Record.doctor_email == doctor_aim.doctor_email).delete()
            db.session.delete(doctor_aim)
            db.session.delete(user_aim)
        if i is None:
            if cid == ' ':
                flash("The Clinic can only be modified when it owns an Clinic ID.")
            else:
                doctor_aim = db.session.query(Doctor).filter(Doctor.clinic_id == cid).first()
                if request.form.get('address') != '':
                    doctor_aim.address = request.form.get('address')
                if request.form.get('gender') != '':
                    doctor_aim.gender = request.form.get('gender')
                if request.form.get('clinic_name') != '':
                    doctor_aim.clinic_name = request.form.get('clinic_name')
                if request.form.get('clinic_phone_number') != '':
                    doctor_aim.clinic_phone_number = request.form.get('clinic_phone_number')
        db.session.commit()
    d = db.session.query(Doctor).filter(Doctor.doctor_email != '').order_by(Doctor.id).all()
    return render_template('admin/admin_doctor.html', doctor=d)


# view function for setting request limit
@admin.route('/admin/appointment/limit', methods=['GET', 'POST'])
@login_required
def request_limit():
    form = RequestLimitForm()
    als = db.session.query(Admin).all()
    admin = db.session.query(Admin).filter(Admin.admin_email == current_user.email).first()
    if form.validate_on_submit():
        for a in als:
            a.request_limit = form.request_limit.data
            db.session.commit()
        return redirect(url_for('admin.admin_patient'))
    elif request.method == 'GET':
        form.request_limit.data = admin.request_limit
    return render_template('admin/request_limit.html', form=form)


def pie_base() -> Pie:
    c = (
        Pie()
        .add("",[list(z) for z in zip(["All Patient", "Already Vaccinated", "Ready for Vaccination", "Not Vaccinated"],
                                      [Patient.query.filter(Patient.patient_email != "").count(),
                                       Patient.query.filter_by(vaccination=2).count(),
                                       Patient.query.filter_by(vaccination=1).count(),
                                       Patient.query.filter_by(vaccination=0).count()])])
        .set_global_opts(title_opts=opts.TitleOpts(title="Statistic Pie", subtitle="Patient"))
    )
    return c


# view function for pie chart
@admin.route("/admin/pie")
@login_required
def admin_pie():
    return render_template('admin/graph.html')


@admin.route("/pieChart")
@login_required
def get_pie_chart():
    c = pie_base()
    return c.dump_options_with_quotes()

