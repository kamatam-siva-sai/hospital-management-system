from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from extensions import db
from models.doctor import Doctor
from routes.decorators import role_required


doctor_bp = Blueprint(
    "doctor",
    __name__,
    url_prefix="/doctors"
)


# -----------------------------
# GET ALL DOCTORS
# -----------------------------
@doctor_bp.route("/", methods=["GET"])
@role_required("admin")
def list_doctors():
    doctors = Doctor.query.all()

    return render_template(
        "doctors/list.html",
        doctors=doctors
    )


# -----------------------------
# SHOW ADD DOCTOR FORM
# -----------------------------
@doctor_bp.route("/new", methods=["GET"])
@role_required("admin")
def new_doctor():
    return render_template("doctors/add.html")


# -----------------------------
# CREATE DOCTOR
# -----------------------------
@doctor_bp.route("/", methods=["POST"])
@role_required("admin")
def create_doctor():

    name = request.form.get("name")
    specialization = request.form.get("specialization")

    if not name or not name.strip():
        return "Doctor name is required", 400

    if not specialization or not specialization.strip():
        return "Specialization is required", 400

    doctor = Doctor(
        name=name.strip(),
        specialization=specialization.strip()
    )

    db.session.add(doctor)
    db.session.commit()

    return redirect(url_for("doctor.list_doctors"))


# -----------------------------
# GET SINGLE DOCTOR
# -----------------------------
@doctor_bp.route("/<int:doctor_id>", methods=["GET"])
@role_required("admin")
def doctor_detail(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    return render_template(
        "doctors/detail.html",
        doctor=doctor
    )


# -----------------------------
# SHOW EDIT DOCTOR FORM
# -----------------------------
@doctor_bp.route("/<int:doctor_id>/edit", methods=["GET"])
@role_required("admin")
def edit_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    return render_template(
        "doctors/edit.html",
        doctor=doctor
    )


# -----------------------------
# UPDATE DOCTOR - PUT
# -----------------------------
@doctor_bp.route(
    "/<int:doctor_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name:
        return jsonify({
            "message": "Name is required"
        }), 400

    if not specialization:
        return jsonify({
            "message": "Specialization is required"
        }), 400

    doctor.name = name.strip()
    doctor.specialization = specialization.strip()

    db.session.commit()

    return jsonify({
        "message": "Doctor updated successfully",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


# -----------------------------
# PARTIAL UPDATE - PATCH
# -----------------------------
@doctor_bp.route(
    "/<int:doctor_id>",
    methods=["PATCH"]
)
@role_required("admin")
def patch_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    if "name" in data:

        if not data["name"] or not data["name"].strip():
            return jsonify({
                "message": "Name cannot be empty"
            }), 400

        doctor.name = data["name"].strip()

    if "specialization" in data:

        if (
            not data["specialization"]
            or not data["specialization"].strip()
        ):
            return jsonify({
                "message": "Specialization cannot be empty"
            }), 400

        doctor.specialization = data["specialization"].strip()

    db.session.commit()

    return jsonify({
        "message": "Doctor partially updated successfully",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


# -----------------------------
# DELETE DOCTOR
# -----------------------------
@doctor_bp.route(
    "/<int:doctor_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    if doctor.appointments:

        return jsonify({
            "message": (
                "Cannot delete doctor because "
                "appointments are associated with this doctor."
            )
        }), 409

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor deleted successfully"
    }), 200