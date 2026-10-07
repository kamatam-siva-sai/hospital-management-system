from datetime import datetime

from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required, get_jwt

from extensions import db
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment
from routes.decorators import role_required


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_current_user_claims():
    return get_jwt()


def patient_to_dict(patient):
    return {
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "contact": patient.contact
    }


def appointment_to_dict(appointment):
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


def doctor_can_access_appointment(appointment):
    claims = get_current_user_claims()

    role = claims.get("role")

    # Admin can access everything
    if role == "admin":
        return True

    # Doctor can access only their appointments
    if role == "doctor":
        doctor_id = claims.get("doctor_id")

        if doctor_id is None:
            return False

        return int(doctor_id) == appointment.doctor_id

    # Patient can access only their appointments
    if role == "patient":
        patient_id = claims.get("patient_id")

        if patient_id is None:
            return False

        return int(patient_id) == appointment.patient_id

    return False


# ============================================================
# PATIENT API
# Admin only
# ============================================================

@api_bp.route("/patients", methods=["GET"])
@role_required("admin")
def get_patients():

    patients = Patient.query.all()

    data = [
        patient_to_dict(patient)
        for patient in patients
    ]

    return jsonify(data), 200


@api_bp.route("/patients", methods=["POST"])
@role_required("admin")
def create_patient():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name:
        return jsonify({
            "message": "Name is required"
        }), 400

    if age is None:
        return jsonify({
            "message": "Age is required"
        }), 400

    if not isinstance(age, int) or age <= 0:
        return jsonify({
            "message": "Age must be a positive integer"
        }), 400

    if not gender:
        return jsonify({
            "message": "Gender is required"
        }), 400

    if not contact:
        return jsonify({
            "message": "Contact is required"
        }), 400

    existing_patient = Patient.query.filter_by(
        contact=str(contact)
    ).first()

    if existing_patient:
        return jsonify({
            "message": "Contact already exists"
        }), 409

    patient = Patient(
        name=name,
        age=age,
        gender=gender,
        contact=str(contact)
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient created successfully",
        "patient": patient_to_dict(patient)
    }), 201


@api_bp.route("/patients/<int:patient_id>", methods=["GET"])
@role_required("admin")
def get_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    return jsonify(patient_to_dict(patient)), 200


@api_bp.route("/patients/<int:patient_id>", methods=["PUT"])
@role_required("admin")
def update_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or age is None or not gender or not contact:
        return jsonify({
            "message": "name, age, gender and contact are required"
        }), 400

    if not isinstance(age, int) or age <= 0:
        return jsonify({
            "message": "Age must be a positive integer"
        }), 400

    existing_patient = Patient.query.filter(
        Patient.contact == str(contact),
        Patient.id != patient_id
    ).first()

    if existing_patient:
        return jsonify({
            "message": "Contact already exists"
        }), 409

    patient.name = name
    patient.age = age
    patient.gender = gender
    patient.contact = str(contact)

    db.session.commit()

    return jsonify({
        "message": "Patient updated successfully",
        "patient": patient_to_dict(patient)
    }), 200


@api_bp.route("/patients/<int:patient_id>", methods=["PATCH"])
@role_required("admin")
def patch_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    if "name" in data:

        if not data["name"]:
            return jsonify({
                "message": "Name cannot be empty"
            }), 400

        patient.name = data["name"]

    if "age" in data:

        if not isinstance(data["age"], int) or data["age"] <= 0:
            return jsonify({
                "message": "Age must be a positive integer"
            }), 400

        patient.age = data["age"]

    if "gender" in data:

        if not data["gender"]:
            return jsonify({
                "message": "Gender cannot be empty"
            }), 400

        patient.gender = data["gender"]

    if "contact" in data:

        if not data["contact"]:
            return jsonify({
                "message": "Contact cannot be empty"
            }), 400

        existing_patient = Patient.query.filter(
            Patient.contact == str(data["contact"]),
            Patient.id != patient_id
        ).first()

        if existing_patient:
            return jsonify({
                "message": "Contact already exists"
            }), 409

        patient.contact = str(data["contact"])

    db.session.commit()

    return jsonify({
        "message": "Patient updated successfully",
        "patient": patient_to_dict(patient)
    }), 200


@api_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
@role_required("admin")
def delete_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    if patient.appointments:
        return jsonify({
            "message": "Cannot delete patient because appointments exist"
        }), 400

    db.session.delete(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient deleted successfully"
    }), 200


# ============================================================
# DOCTOR API
# Admin only
# ============================================================

@api_bp.route("/doctors", methods=["GET"])
@role_required("admin")
def get_doctors():

    doctors = Doctor.query.all()

    data = []

    for doctor in doctors:

        data.append({
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        })

    return jsonify(data), 200


@api_bp.route("/doctors", methods=["POST"])
@role_required("admin")
def create_doctor():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name:
        return jsonify({
            "message": "Doctor name is required"
        }), 400

    if not specialization:
        return jsonify({
            "message": "Specialization is required"
        }), 400

    doctor = Doctor(
        name=name,
        specialization=specialization
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor created successfully",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 201


@api_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
@role_required("admin")
def get_doctor(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    return jsonify({
        "id": doctor.id,
        "name": doctor.name,
        "specialization": doctor.specialization
    }), 200


@api_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@role_required("admin")
def update_doctor(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name or not specialization:
        return jsonify({
            "message": "name and specialization are required"
        }), 400

    doctor.name = name
    doctor.specialization = specialization

    db.session.commit()

    return jsonify({
        "message": "Doctor updated successfully",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


@api_bp.route("/doctors/<int:doctor_id>", methods=["PATCH"])
@role_required("admin")
def patch_doctor(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    if "name" in data:

        if not data["name"]:
            return jsonify({
                "message": "Name cannot be empty"
            }), 400

        doctor.name = data["name"]

    if "specialization" in data:

        if not data["specialization"]:
            return jsonify({
                "message": "Specialization cannot be empty"
            }), 400

        doctor.specialization = data["specialization"]

    db.session.commit()

    return jsonify({
        "message": "Doctor updated successfully",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


@api_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
@role_required("admin")
def delete_doctor(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    if doctor.appointments:
        return jsonify({
            "message": "Cannot delete doctor because appointments exist"
        }), 400

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor deleted successfully"
    }), 200


# ============================================================
# PATIENT SELF-SERVICE API
# Patient only
# ============================================================

@api_bp.route("/patient/profile", methods=["GET"])
@jwt_required()
def patient_profile():

    claims = get_current_user_claims()

    if claims.get("role") != "patient":
        return jsonify({
            "message": "Access denied. Patient login required."
        }), 403

    patient_id = claims.get("patient_id")

    if patient_id is None:
        return jsonify({
            "message": "Patient account is not linked to a patient record"
        }), 403

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    return jsonify({
        "message": "Patient profile retrieved successfully",
        "patient": patient_to_dict(patient)
    }), 200


@api_bp.route("/patient/appointments", methods=["GET"])
@jwt_required()
def patient_appointments():

    claims = get_current_user_claims()

    if claims.get("role") != "patient":
        return jsonify({
            "message": "Access denied. Patient login required."
        }), 403

    patient_id = claims.get("patient_id")

    if patient_id is None:
        return jsonify({
            "message": "Patient account is not linked to a patient record"
        }), 403

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).all()

    data = [
        appointment_to_dict(appointment)
        for appointment in appointments
    ]

    return jsonify({
        "message": "Patient appointments retrieved successfully",
        "appointments": data
    }), 200


@api_bp.route(
    "/patient/appointments/<int:appointment_id>",
    methods=["GET"]
)
@jwt_required()
def patient_appointment(appointment_id):

    claims = get_current_user_claims()

    if claims.get("role") != "patient":
        return jsonify({
            "message": "Access denied. Patient login required."
        }), 403

    patient_id = claims.get("patient_id")

    if patient_id is None:
        return jsonify({
            "message": "Patient account is not linked to a patient record"
        }), 403

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    if appointment.patient_id != int(patient_id):
        return jsonify({
            "message": "Access denied. You can only view your own appointments."
        }), 403

    return jsonify(
        appointment_to_dict(appointment)
    ), 200


# ============================================================
# APPOINTMENT API
# Admin + Doctor-specific access
# ============================================================

@api_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():

    claims = get_current_user_claims()
    role = claims.get("role")

    if role == "admin":

        appointments = Appointment.query.all()

    elif role == "doctor":

        doctor_id = claims.get("doctor_id")

        if doctor_id is None:
            return jsonify({
                "message": "Doctor account is not linked to a doctor record"
            }), 403

        appointments = Appointment.query.filter_by(
            doctor_id=doctor_id
        ).all()

    elif role == "patient":

        patient_id = claims.get("patient_id")

        if patient_id is None:
            return jsonify({
                "message": "Patient account is not linked to a patient record"
            }), 403

        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).all()

    else:

        return jsonify({
            "message": "Access denied"
        }), 403

    data = [
        appointment_to_dict(appointment)
        for appointment in appointments
    ]

    return jsonify(data), 200


@api_bp.route("/appointments", methods=["POST"])
@role_required("admin")
def create_appointment():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    date_string = data.get("date")
    diagnosis = data.get("diagnosis")
    status = data.get("status", "Under Treatment")

    if patient_id is None:
        return jsonify({
            "message": "patient_id is required"
        }), 400

    if doctor_id is None:
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

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=appointment_date,
        diagnosis=diagnosis,
        status=status
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment created successfully",
        "appointment": appointment_to_dict(appointment)
    }), 201


@api_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["GET"]
)
@jwt_required()
def get_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    if not doctor_can_access_appointment(appointment):

        return jsonify({
            "message": "Access denied. You can only view your own appointments."
        }), 403

    return jsonify(
        appointment_to_dict(appointment)
    ), 200


@api_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["PUT"]
)
@jwt_required()
def update_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    claims = get_current_user_claims()
    role = claims.get("role")

    # Patients cannot edit appointments
    if role == "patient":
        return jsonify({
            "message": "Patients can only view appointments."
        }), 403

    if not doctor_can_access_appointment(appointment):

        return jsonify({
            "message": "Access denied. You can only edit your own appointments."
        }), 403

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

    if patient_id is None:
        return jsonify({
            "message": "patient_id is required"
        }), 400

    if doctor_id is None:
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

    # Doctor cannot move appointment to another doctor
    if role == "doctor":

        if int(doctor_id) != int(claims.get("doctor_id")):

            return jsonify({
                "message": (
                    "Doctors can only keep appointments "
                    "assigned to themselves"
                )
            }), 403

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
        "appointment": appointment_to_dict(appointment)
    }), 200


@api_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["PATCH"]
)
@jwt_required()
def patch_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    claims = get_current_user_claims()
    role = claims.get("role")

    # Patients cannot edit appointments
    if role == "patient":
        return jsonify({
            "message": "Patients can only view appointments."
        }), 403

    if not doctor_can_access_appointment(appointment):

        return jsonify({
            "message": "Access denied. You can only edit your own appointments."
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    if "patient_id" in data:

        patient = Patient.query.get(
            data["patient_id"]
        )

        if not patient:
            return jsonify({
                "message": "Patient not found"
            }), 404

        appointment.patient_id = data["patient_id"]

    if "doctor_id" in data:

        doctor = Doctor.query.get(
            data["doctor_id"]
        )

        if not doctor:
            return jsonify({
                "message": "Doctor not found"
            }), 404

        if role == "doctor":

            if int(data["doctor_id"]) != int(
                claims.get("doctor_id")
            ):

                return jsonify({
                    "message": (
                        "Doctors cannot assign "
                        "appointments to another doctor"
                    )
                }), 403

        appointment.doctor_id = data["doctor_id"]

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

    if "diagnosis" in data:

        if not data["diagnosis"]:
            return jsonify({
                "message": "Diagnosis cannot be empty"
            }), 400

        appointment.diagnosis = data["diagnosis"]

    if "status" in data:

        if not data["status"]:
            return jsonify({
                "message": "Status cannot be empty"
            }), 400

        appointment.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "Appointment updated successfully",
        "appointment": appointment_to_dict(appointment)
    }), 200


@api_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment deleted successfully"
    }), 200