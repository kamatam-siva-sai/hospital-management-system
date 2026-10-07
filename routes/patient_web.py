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
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment


patient_web_bp = Blueprint(
    "patient_web",
    __name__
)


# ============================================================
# PATIENT ACCESS
# ============================================================

def patient_web_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("web_auth.web_login")
            )

        if session.get("user_role") != "patient":
            return (
                "Access denied. Patient access required.",
                403
            )

        if not session.get("patient_id"):
            return (
                "Patient account is not linked to a patient record.",
                403
            )

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# PATIENT DASHBOARD
# ============================================================

@patient_web_bp.route(
    "/patient-dashboard",
    methods=["GET"]
)
@patient_web_required
def patient_dashboard():

    patient_id = session.get("patient_id")

    patient = Patient.query.get(patient_id)

    if not patient:
        session.clear()

        return redirect(
            url_for("web_auth.web_login")
        )

    appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).order_by(
        Appointment.date.desc()
    ).all()

    doctors = Doctor.query.order_by(
        Doctor.name.asc()
    ).all()

    return render_template(
        "patient/dashboard.html",
        patient=patient,
        appointments=appointments,
        doctors=doctors
    )


# ============================================================
# BOOK APPOINTMENT
# ============================================================

@patient_web_bp.route(
    "/patient-appointments/book",
    methods=["POST"]
)
@patient_web_required
def book_appointment():

    patient_id = session.get("patient_id")

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


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not doctor_id:

        flash(
            "Please select a doctor.",
            "error"
        )

        return redirect(
            url_for("patient_web.patient_dashboard")
        )


    if not date_string:

        flash(
            "Please select an appointment date.",
            "error"
        )

        return redirect(
            url_for("patient_web.patient_dashboard")
        )


    if not diagnosis:

        flash(
            "Please enter the reason for the appointment.",
            "error"
        )

        return redirect(
            url_for("patient_web.patient_dashboard")
        )


    # --------------------------------------------------------
    # CHECK PATIENT
    # --------------------------------------------------------

    patient = Patient.query.get(
        patient_id
    )

    if not patient:

        flash(
            "Patient record not found.",
            "error"
        )

        return redirect(
            url_for("web_auth.web_login")
        )


    # --------------------------------------------------------
    # CHECK DOCTOR
    # --------------------------------------------------------

    doctor = Doctor.query.get(
        int(doctor_id)
    )

    if not doctor:

        flash(
            "Selected doctor was not found.",
            "error"
        )

        return redirect(
            url_for("patient_web.patient_dashboard")
        )


    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    try:

        appointment_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Invalid appointment date.",
            "error"
        )

        return redirect(
            url_for("patient_web.patient_dashboard")
        )


    # --------------------------------------------------------
    # PREVENT PAST DATE
    # --------------------------------------------------------

    from datetime import date

    if appointment_date < date.today():

        flash(
            "Appointment date cannot be in the past.",
            "error"
        )

        return redirect(
            url_for("patient_web.patient_dashboard")
        )


    # --------------------------------------------------------
    # CREATE APPOINTMENT
    # --------------------------------------------------------

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        date=appointment_date,
        diagnosis=diagnosis,
        status="Scheduled"
    )

    db.session.add(appointment)

    db.session.commit()


    flash(
        "Appointment booked successfully.",
        "success"
    )

    return redirect(
        url_for("patient_web.patient_dashboard")
    )


# ============================================================
# PATIENT LOGOUT
# ============================================================

@patient_web_bp.route(
    "/patient-logout",
    methods=["GET"]
)
def patient_logout():

    session.clear()

    return redirect(
        url_for("web_auth.web_login")
    )