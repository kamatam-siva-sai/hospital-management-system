from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from extensions import db
from models.patient import Patient
from routes.decorators import role_required


patient_bp = Blueprint(
    "patient",
    __name__,
    url_prefix="/patients"
)


# ==========================================
# GET ALL PATIENTS
# ==========================================
@patient_bp.route("/", methods=["GET"])
@role_required("admin")
def list_patients():

    patients = Patient.query.all()

    return render_template(
        "patients/list.html",
        patients=patients
    )


# ==========================================
# SHOW ADD PATIENT FORM
# ==========================================
@patient_bp.route("/new", methods=["GET"])
@role_required("admin")
def new_patient():

    return render_template(
        "patients/add.html"
    )


# ==========================================
# CREATE PATIENT
# ==========================================
@patient_bp.route("/", methods=["POST"])
@role_required("admin")
def create_patient():

    name = request.form.get("name")
    age = request.form.get("age")
    gender = request.form.get("gender")
    contact = request.form.get("contact")

    if not name or not name.strip():
        return "Patient name is required", 400

    if not age:
        return "Age is required", 400

    if not gender:
        return "Gender is required", 400

    if not contact or not contact.strip():
        return "Contact is required", 400

    try:
        age = int(age)
    except ValueError:
        return "Age must be a number", 400

    if age <= 0:
        return "Age must be greater than 0", 400

    existing_patient = Patient.query.filter_by(
        contact=contact.strip()
    ).first()

    if existing_patient:
        return "Contact already exists", 409

    patient = Patient(
        name=name.strip(),
        age=age,
        gender=gender.strip(),
        contact=contact.strip()
    )

    db.session.add(patient)
    db.session.commit()

    return redirect(
        url_for("patient.list_patients")
    )


# ==========================================
# PATIENT DETAILS
# ==========================================
@patient_bp.route("/<int:patient_id>", methods=["GET"])
@role_required("admin")
def patient_detail(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    return render_template(
        "patients/detail.html",
        patient=patient
    )


# ==========================================
# EDIT FORM
# ==========================================
@patient_bp.route("/<int:patient_id>/edit", methods=["GET"])
@role_required("admin")
def edit_patient(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    return render_template(
        "patients/edit.html",
        patient=patient
    )


# ==========================================
# FULL UPDATE - PUT
# ==========================================
@patient_bp.route(
    "/<int:patient_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_patient(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or age is None or not gender or not contact:
        return jsonify({
            "message": "name, age, gender and contact are required"
        }), 400

    try:
        age = int(age)
    except ValueError:
        return jsonify({
            "message": "Age must be a number"
        }), 400

    existing_patient = Patient.query.filter(
        Patient.contact == contact,
        Patient.id != patient_id
    ).first()

    if existing_patient:
        return jsonify({
            "message": "Contact already exists"
        }), 409

    patient.name = name
    patient.age = age
    patient.gender = gender
    patient.contact = contact

    db.session.commit()

    return jsonify({
        "message": "Patient updated successfully",
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 200


# ==========================================
# PARTIAL UPDATE - PATCH
# ==========================================
@patient_bp.route(
    "/<int:patient_id>",
    methods=["PATCH"]
)
@role_required("admin")
def patch_patient(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    if "name" in data:
        patient.name = data["name"]

    if "age" in data:
        try:
            patient.age = int(data["age"])
        except ValueError:
            return jsonify({
                "message": "Age must be a number"
            }), 400

    if "gender" in data:
        patient.gender = data["gender"]

    if "contact" in data:

        existing_patient = Patient.query.filter(
            Patient.contact == data["contact"],
            Patient.id != patient_id
        ).first()

        if existing_patient:
            return jsonify({
                "message": "Contact already exists"
            }), 409

        patient.contact = data["contact"]

    db.session.commit()

    return jsonify({
        "message": "Patient partially updated successfully",
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 200


# ==========================================
# DELETE PATIENT
# ==========================================
@patient_bp.route(
    "/<int:patient_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_patient(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    if patient.appointments:
        return jsonify({
            "message": (
                "Cannot delete patient because "
                "appointments are associated with this patient."
            )
        }), 409

    db.session.delete(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient deleted successfully"
    }), 200