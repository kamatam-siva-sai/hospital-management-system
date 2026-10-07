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
from models.patient import Patient


# ==================================================
# BLUEPRINT
# ==================================================

admin_patient_web_bp = Blueprint(
    "admin_patient_web",
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
# PATIENT LIST
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients",
    methods=["GET"]
)
@admin_web_required
def admin_patient_list():

    patients = Patient.query.order_by(
        Patient.id.asc()
    ).all()

    return render_template(
        "patients/list.html",
        patients=patients
    )


# ==================================================
# ADD PATIENT - GET
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients/new",
    methods=["GET"]
)
@admin_web_required
def admin_patient_new():

    return render_template(
        "patients/new.html"
    )


# ==================================================
# ADD PATIENT - POST
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients/new",
    methods=["POST"]
)
@admin_web_required
def admin_patient_create():

    name = request.form.get(
        "name",
        ""
    ).strip()

    age = request.form.get(
        "age",
        ""
    ).strip()

    gender = request.form.get(
        "gender",
        ""
    ).strip()

    contact = request.form.get(
        "contact",
        ""
    ).strip()


    if not name:

        return render_template(
            "patients/new.html",
            error="Patient name is required."
        )


    if not age:

        return render_template(
            "patients/new.html",
            error="Age is required."
        )


    if not gender:

        return render_template(
            "patients/new.html",
            error="Gender is required."
        )


    if not contact:

        return render_template(
            "patients/new.html",
            error="Contact number is required."
        )


    # Validate age

    try:

        age = int(age)

    except ValueError:

        return render_template(
            "patients/new.html",
            error="Age must be a valid number."
        )


    if age <= 0 or age > 120:

        return render_template(
            "patients/new.html",
            error="Age must be between 1 and 120."
        )


    # Check duplicate contact

    existing_patient = Patient.query.filter_by(
        contact=contact
    ).first()

    if existing_patient:

        return render_template(
            "patients/new.html",
            error=(
                "A patient with this contact number "
                "already exists."
            )
        )


    # Create patient

    patient = Patient(
        name=name,
        age=age,
        gender=gender,
        contact=contact
    )

    db.session.add(patient)
    db.session.commit()


    flash(
        "Patient added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_patient_web.admin_patient_list"
        )
    )


# ==================================================
# VIEW PATIENT
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients/<int:patient_id>",
    methods=["GET"]
)
@admin_web_required
def admin_patient_view(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:

        return (
            "Patient not found.",
            404
        )


    return render_template(
        "patients/detail.html",
        patient=patient
    )


# ==================================================
# EDIT PATIENT - GET
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients/<int:patient_id>/edit",
    methods=["GET"]
)
@admin_web_required
def admin_patient_edit(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:

        return (
            "Patient not found.",
            404
        )


    return render_template(
        "patients/edit.html",
        patient=patient
    )


# ==================================================
# EDIT PATIENT - POST
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients/<int:patient_id>/edit",
    methods=["POST"]
)
@admin_web_required
def admin_patient_update(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:

        return (
            "Patient not found.",
            404
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    age = request.form.get(
        "age",
        ""
    ).strip()

    gender = request.form.get(
        "gender",
        ""
    ).strip()

    contact = request.form.get(
        "contact",
        ""
    ).strip()


    if not name:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error="Patient name is required."
        )


    if not age:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error="Age is required."
        )


    if not gender:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error="Gender is required."
        )


    if not contact:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error="Contact number is required."
        )


    # Validate age

    try:

        age = int(age)

    except ValueError:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error="Age must be a valid number."
        )


    if age <= 0 or age > 120:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error="Age must be between 1 and 120."
        )


    # Check duplicate contact

    existing_patient = Patient.query.filter(
        Patient.contact == contact,
        Patient.id != patient.id
    ).first()


    if existing_patient:

        return render_template(
            "patients/edit.html",
            patient=patient,
            error=(
                "Another patient already uses "
                "this contact number."
            )
        )


    # Update patient

    patient.name = name
    patient.age = age
    patient.gender = gender
    patient.contact = contact


    db.session.commit()


    flash(
        "Patient updated successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_patient_web.admin_patient_list"
        )
    )


# ==================================================
# DELETE PATIENT
# ==================================================

@admin_patient_web_bp.route(
    "/admin/patients/<int:patient_id>/delete",
    methods=["POST"]
)
@admin_web_required
def admin_patient_delete(patient_id):

    patient = Patient.query.get(patient_id)


    if not patient:

        flash(
            "Patient not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_patient_web.admin_patient_list"
            )
        )


    # Do not delete patients who have appointments

    if patient.appointments:

        flash(
            (
                "Cannot delete this patient because "
                "appointments are linked to this patient."
            ),
            "error"
        )

        return redirect(
            url_for(
                "admin_patient_web.admin_patient_list"
            )
        )


    db.session.delete(patient)

    db.session.commit()


    flash(
        "Patient deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_patient_web.admin_patient_list"
        )
    )