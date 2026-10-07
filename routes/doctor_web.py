from functools import wraps

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
from models.doctor import Doctor


doctor_web_bp = Blueprint(
    "doctor_web",
    __name__
)


# ============================================================
# DOCTOR ACCESS
# ============================================================

def doctor_web_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("web_auth.web_login")
            )

        if session.get("user_role") != "doctor":
            return (
                "Access denied. Doctor access required.",
                403
            )

        if not session.get("doctor_id"):
            return (
                "Doctor account is not linked to a doctor record.",
                403
            )

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

@doctor_web_bp.route(
    "/doctor-dashboard",
    methods=["GET"]
)
@doctor_web_required
def doctor_dashboard():

    doctor_id = session.get("doctor_id")

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        session.clear()

        return redirect(
            url_for("web_auth.web_login")
        )

    appointments = Appointment.query.filter_by(
        doctor_id=doctor_id
    ).order_by(
        Appointment.date.desc()
    ).all()

    return render_template(
        "doctor/dashboard.html",
        doctor=doctor,
        appointments=appointments
    )


# ============================================================
# EDIT DOCTOR APPOINTMENT
# ============================================================

@doctor_web_bp.route(
    "/doctor-appointment/<int:appointment_id>/edit",
    methods=["GET", "POST"]
)
@doctor_web_required
def doctor_edit_appointment(appointment_id):

    doctor_id = session.get("doctor_id")

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        session.clear()

        return redirect(
            url_for("web_auth.web_login")
        )

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor_id
    ).first()

    if not appointment:
        return (
            "Appointment not found or access denied.",
            404
        )

    if request.method == "POST":

        diagnosis = request.form.get(
            "diagnosis",
            ""
        ).strip()

        status = request.form.get(
            "status",
            ""
        ).strip()

        if not diagnosis:

            return render_template(
                "doctor/edit_appointment.html",
                doctor=doctor,
                appointment=appointment,
                error="Diagnosis is required."
            )

        if not status:

            return render_template(
                "doctor/edit_appointment.html",
                doctor=doctor,
                appointment=appointment,
                error="Status is required."
            )

        appointment.diagnosis = diagnosis
        appointment.status = status

        db.session.commit()

        flash(
            "Appointment updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "doctor_web.doctor_dashboard"
            )
        )

    return render_template(
        "doctor/edit_appointment.html",
        doctor=doctor,
        appointment=appointment
    )


# ============================================================
# DOCTOR LOGOUT
# ============================================================

@doctor_web_bp.route(
    "/doctor-logout",
    methods=["GET"]
)
def doctor_logout():

    session.clear()

    return redirect(
        url_for("web_auth.web_login")
    )