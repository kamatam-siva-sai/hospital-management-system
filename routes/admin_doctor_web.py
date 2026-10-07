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
from models.doctor import Doctor


# ==================================================
# BLUEPRINT
# ==================================================

admin_doctor_web_bp = Blueprint(
    "admin_doctor_web",
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
# DOCTOR LIST
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors",
    methods=["GET"]
)
@admin_web_required
def admin_doctor_list():

    doctors = Doctor.query.order_by(
        Doctor.id.asc()
    ).all()

    return render_template(
        "doctors/list.html",
        doctors=doctors
    )


# ==================================================
# ADD DOCTOR - GET
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors/new",
    methods=["GET"]
)
@admin_web_required
def admin_doctor_new():

    return render_template(
        "doctors/new.html"
    )


# ==================================================
# ADD DOCTOR - POST
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors/new",
    methods=["POST"]
)
@admin_web_required
def admin_doctor_create():

    name = request.form.get(
        "name",
        ""
    ).strip()

    specialization = request.form.get(
        "specialization",
        ""
    ).strip()


    if not name:

        return render_template(
            "doctors/new.html",
            error="Doctor name is required."
        )


    if not specialization:

        return render_template(
            "doctors/new.html",
            error="Specialization is required."
        )


    doctor = Doctor(
        name=name,
        specialization=specialization
    )


    db.session.add(doctor)

    db.session.commit()


    flash(
        "Doctor added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_doctor_web.admin_doctor_list"
        )
    )


# ==================================================
# VIEW DOCTOR
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors/<int:doctor_id>",
    methods=["GET"]
)
@admin_web_required
def admin_doctor_view(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:

        return (
            "Doctor not found.",
            404
        )


    return render_template(
        "doctors/detail.html",
        doctor=doctor
    )


# ==================================================
# EDIT DOCTOR - GET
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors/<int:doctor_id>/edit",
    methods=["GET"]
)
@admin_web_required
def admin_doctor_edit(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:

        return (
            "Doctor not found.",
            404
        )


    return render_template(
        "doctors/edit.html",
        doctor=doctor
    )


# ==================================================
# EDIT DOCTOR - POST
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors/<int:doctor_id>/edit",
    methods=["POST"]
)
@admin_web_required
def admin_doctor_update(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:

        return (
            "Doctor not found.",
            404
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    specialization = request.form.get(
        "specialization",
        ""
    ).strip()


    if not name:

        return render_template(
            "doctors/edit.html",
            doctor=doctor,
            error="Doctor name is required."
        )


    if not specialization:

        return render_template(
            "doctors/edit.html",
            doctor=doctor,
            error="Specialization is required."
        )


    doctor.name = name

    doctor.specialization = specialization


    try:

        db.session.commit()

    except Exception as error:

        db.session.rollback()

        return render_template(
            "doctors/edit.html",
            doctor=doctor,
            error=f"Unable to update doctor: {error}"
        )


    flash(
        "Doctor updated successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_doctor_web.admin_doctor_list"
        )
    )


# ==================================================
# DELETE DOCTOR
# ==================================================

@admin_doctor_web_bp.route(
    "/admin/doctors/<int:doctor_id>/delete",
    methods=["POST"]
)
@admin_web_required
def admin_doctor_delete(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:

        flash(
            "Doctor not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin_doctor_web.admin_doctor_list"
            )
        )


    # Doctor has appointments

    if doctor.appointments:

        flash(
            (
                "Cannot delete this doctor because "
                "appointments are linked to this doctor."
            ),
            "error"
        )

        return redirect(
            url_for(
                "admin_doctor_web.admin_doctor_list"
            )
        )


    # Doctor has login account

    if doctor.user:

        flash(
            (
                "Cannot delete this doctor because "
                "a login account is linked to this doctor."
            ),
            "error"
        )

        return redirect(
            url_for(
                "admin_doctor_web.admin_doctor_list"
            )
        )


    db.session.delete(doctor)

    db.session.commit()


    flash(
        "Doctor deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin_doctor_web.admin_doctor_list"
        )
    )