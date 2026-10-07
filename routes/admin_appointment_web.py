from functools import wraps
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    flash
)

from extensions import db
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor


# ==================================================
# BLUEPRINT
# ==================================================

admin_appointment_web_bp = Blueprint(
    "admin_appointment_web",
    __name__
)


# ==================================================
# ADMIN LOGIN CHECK
# ==================================================

def admin_web_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("web_auth.web_login")
            )

        if session.get("user_role") != "admin":
            return (
                "Access denied. Admin access required.",
                403
            )

        return function(*args, **kwargs)

    return wrapper


# ==================================================
# APPOINTMENT DASHBOARD
# ==================================================

@admin_appointment_web_bp.route(
    "/admin/appointments",
    methods=["GET"]
)
@admin_web_required
def admin_appointment_dashboard():

    appointments = Appointment.query.order_by(
        Appointment.date.desc()
    ).all()

    patients = Patient.query.order_by(
        Patient.name.asc()
    ).all()

    doctors = Doctor.query.order_by(
        Doctor.name.asc()
    ).all()

    edit_id = request.args.get(
        "edit_id",
        type=int
    )

    edit_appointment = None

    if edit_id:

        edit_appointment = Appointment.query.get(
            edit_id
        )

    view_id = request.args.get(
        "view_id",
        type=int
    )

    view_appointment = None

    if view_id:

        view_appointment = Appointment.query.get(
            view_id
        )

    return render_template(
        "admin_appointments/dashboard.html",
        appointments=appointments,
        patients=patients,
        doctors=doctors,
        edit_appointment=edit_appointment,
        view_appointment=view_appointment
    )


# ==================================================
# ADD APPOINTMENT
# ==================================================

@admin_appointment_web_bp.route(
    "/admin/appointments/add",
    methods=["POST"]
)
@admin_web_required
def admin_appointment_add():

    patient_id = request.form.get(
        "patient_id",
        ""
    ).strip()

    doctor_id = request.form.get(
        "doctor_id",
        ""
    ).strip()

    date_string = request.form.get(
        "date",
        ""
    ).strip()

    diagnosis = request.form.get(
        "diagnosis",
        ""
    ).strip()

    status = request.form.get(
        "status",
        "Under Treatment"
    ).strip()


    if not patient_id:
        flash(
            "Patient is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    if not doctor_id:
        flash(
            "Doctor is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    if not date_string:
        flash(
            "Date is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    if not diagnosis:
        flash(
            "Diagnosis is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    patient = Patient.query.get(
        patient_id
    )

    if not patient:

        flash(
            "Patient not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    doctor = Doctor.query.get(
        doctor_id
    )

    if not doctor:

        flash(
            "Doctor not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    try:

        appointment_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Date must be in YYYY-MM-DD format.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        date=appointment_date,
        diagnosis=diagnosis,
        status=status
    )


    db.session.add(
        appointment
    )

    db.session.commit()


    flash(
        "Appointment added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_appointment_web.admin_appointment_dashboard"
        )
    )


# ==================================================
# UPDATE APPOINTMENT
# ==================================================

@admin_appointment_web_bp.route(
    "/admin/appointments/update/<int:appointment_id>",
    methods=["POST"]
)
@admin_web_required
def admin_appointment_update(
    appointment_id
):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:

        flash(
            "Appointment not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    patient_id = request.form.get(
        "patient_id",
        ""
    ).strip()

    doctor_id = request.form.get(
        "doctor_id",
        ""
    ).strip()

    date_string = request.form.get(
        "date",
        ""
    ).strip()

    diagnosis = request.form.get(
        "diagnosis",
        ""
    ).strip()

    status = request.form.get(
        "status",
        ""
    ).strip()


    if not patient_id:
        flash(
            "Patient is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    if not doctor_id:
        flash(
            "Doctor is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    if not date_string:
        flash(
            "Date is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    if not diagnosis:
        flash(
            "Diagnosis is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    if not status:
        flash(
            "Status is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    patient = Patient.query.get(
        patient_id
    )

    if not patient:

        flash(
            "Patient not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    doctor = Doctor.query.get(
        doctor_id
    )

    if not doctor:

        flash(
            "Doctor not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    try:

        appointment_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Date must be in YYYY-MM-DD format.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard",
                edit_id=appointment_id
            )
        )


    appointment.patient_id = patient.id
    appointment.doctor_id = doctor.id
    appointment.date = appointment_date
    appointment.diagnosis = diagnosis
    appointment.status = status


    db.session.commit()


    flash(
        "Appointment updated successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_appointment_web.admin_appointment_dashboard"
        )
    )


# ==================================================
# DELETE APPOINTMENT
# ==================================================

@admin_appointment_web_bp.route(
    "/admin/appointments/delete/<int:appointment_id>",
    methods=["POST"]
)
@admin_web_required
def admin_appointment_delete(
    appointment_id
):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:

        flash(
            "Appointment not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_appointment_web.admin_appointment_dashboard"
            )
        )


    db.session.delete(
        appointment
    )

    db.session.commit()


    flash(
        "Appointment deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_appointment_web.admin_appointment_dashboard"
        )
    )