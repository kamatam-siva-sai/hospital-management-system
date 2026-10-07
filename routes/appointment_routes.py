from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, redirect, url_for

from extensions import db
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor
from routes.decorators import role_required


# ============================================================
# BLUEPRINT
# ============================================================

appointment_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/appointments"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_appointment_data(appointment):
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "patient_name": appointment.patient.name,
        "doctor_id": appointment.doctor_id,
        "doctor_name": appointment.doctor.name,
        "date": appointment.date.strftime("%Y-%m-%d"),
        "diagnosis": appointment.diagnosis,
        "status": appointment.status
    }


# ============================================================
# LIST APPOINTMENTS
# ============================================================

@appointment_bp.route("/", methods=["GET"])
@role_required("admin")
def list_appointments():
    appointments = Appointment.query.all()

    return render_template(
        "appointments/list.html",
        appointments=appointments
    )


# ============================================================
# NEW APPOINTMENT FORM
# ============================================================

@appointment_bp.route("/new", methods=["GET"])
@role_required("admin")
def new_appointment():
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template(
        "appointments/new.html",
        patients=patients,
        doctors=doctors
    )


# ============================================================
# CREATE APPOINTMENT
# ============================================================

@appointment_bp.route("/", methods=["POST"])
@role_required("admin")
def create_appointment():

    patient_id = request.form.get("patient_id")
    doctor_id = request.form.get("doctor_id")
    date_string = request.form.get("date")
    diagnosis = request.form.get("diagnosis")
    status = request.form.get(
        "status",
        "Under Treatment"
    )

    # -------------------------
    # Validation
    # -------------------------

    if not patient_id:
        return jsonify({
            "message": "Patient is required"
        }), 400

    if not doctor_id:
        return jsonify({
            "message": "Doctor is required"
        }), 400

    if not date_string:
        return jsonify({
            "message": "Date is required"
        }), 400

    if not diagnosis:
        return jsonify({
            "message": "Diagnosis is required"
        }), 400

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    try:
        appointment_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return jsonify({
            "message": "Date must be in YYYY-MM-DD format"
        }), 400

    # -------------------------
    # Create appointment
    # -------------------------

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        date=appointment_date,
        diagnosis=diagnosis,
        status=status
    )

    db.session.add(appointment)
    db.session.commit()

    return redirect(
        url_for("appointments.list_appointments")
    )


# ============================================================
# VIEW APPOINTMENT
# ============================================================

@appointment_bp.route("/<int:appointment_id>", methods=["GET"])
@role_required("admin")
def view_appointment(appointment_id):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    return render_template(
        "appointments/detail.html",
        appointment=appointment
    )


# ============================================================
# EDIT APPOINTMENT FORM
# ============================================================

@appointment_bp.route(
    "/<int:appointment_id>/edit",
    methods=["GET"]
)
@role_required("admin")
def edit_appointment(appointment_id):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template(
        "appointments/edit.html",
        appointment=appointment,
        patients=patients,
        doctors=doctors
    )


# ============================================================
# UPDATE APPOINTMENT - PUT
# ============================================================

@appointment_bp.route(
    "/<int:appointment_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_appointment(appointment_id):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    date_string = data.get("date")
    diagnosis = data.get("diagnosis")
    status = data.get("status")

    if not patient_id:
        return jsonify({
            "message": "patient_id is required"
        }), 400

    if not doctor_id:
        return jsonify({
            "message": "doctor_id is required"
        }), 400

    if not date_string:
        return jsonify({
            "message": "date is required"
        }), 400

    if not diagnosis:
        return jsonify({
            "message": "diagnosis is required"
        }), 400

    if not status:
        return jsonify({
            "message": "status is required"
        }), 400

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    try:
        appointment_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return jsonify({
            "message": "Date must be in YYYY-MM-DD format"
        }), 400

    appointment.patient_id = patient_id
    appointment.doctor_id = doctor_id
    appointment.date = appointment_date
    appointment.diagnosis = diagnosis
    appointment.status = status

    db.session.commit()

    return jsonify({
        "message": "Appointment updated successfully",
        "appointment": get_appointment_data(
            appointment
        )
    }), 200


# ============================================================
# PATCH APPOINTMENT
# ============================================================

@appointment_bp.route(
    "/<int:appointment_id>",
    methods=["PATCH"]
)
@role_required("admin")
def patch_appointment(appointment_id):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    # -------------------------
    # Patient
    # -------------------------

    if "patient_id" in data:

        patient = Patient.query.get(
            data["patient_id"]
        )

        if not patient:
            return jsonify({
                "message": "Patient not found"
            }), 404

        appointment.patient_id = data["patient_id"]

    # -------------------------
    # Doctor
    # -------------------------

    if "doctor_id" in data:

        doctor = Doctor.query.get(
            data["doctor_id"]
        )

        if not doctor:
            return jsonify({
                "message": "Doctor not found"
            }), 404

        appointment.doctor_id = data["doctor_id"]

    # -------------------------
    # Date
    # -------------------------

    if "date" in data:

        try:
            appointment.date = datetime.strptime(
                data["date"],
                "%Y-%m-%d"
            ).date()

        except ValueError:
            return jsonify({
                "message": "Date must be in YYYY-MM-DD format"
            }), 400

    # -------------------------
    # Diagnosis
    # -------------------------

    if "diagnosis" in data:

        if not data["diagnosis"]:
            return jsonify({
                "message": "Diagnosis cannot be empty"
            }), 400

        appointment.diagnosis = data["diagnosis"]

    # -------------------------
    # Status
    # -------------------------

    if "status" in data:

        if not data["status"]:
            return jsonify({
                "message": "Status cannot be empty"
            }), 400

        appointment.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "Appointment updated successfully",
        "appointment": get_appointment_data(
            appointment
        )
    }), 200


# ============================================================
# DELETE APPOINTMENT
# ============================================================

@appointment_bp.route(
    "/<int:appointment_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_appointment(appointment_id):

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment deleted successfully"
    }), 200