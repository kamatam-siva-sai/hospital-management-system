from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request
)

from models.user import User


web_auth_bp = Blueprint("web_auth", __name__)


def redirect_by_role(user):

    if user.role == "admin":
        return redirect(
            url_for("analytics.analytics_dashboard")
        )

    if user.role == "doctor":
        return redirect(
            url_for("doctor_web.doctor_dashboard")
        )

    if user.role == "patient":
        return redirect(
            url_for("patient_web.patient_dashboard")
        )

    session.clear()

    return redirect(
        url_for("web_auth.web_login")
    )


@web_auth_bp.route("/web-login", methods=["GET", "POST"])
def web_login():

    # Only process login when the form is submitted
    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = None

        if not email:
            error = "Email is required."

        elif not password:
            error = "Password is required."

        else:

            user = User.query.filter_by(
                email=email
            ).first()

            if not user:

                error = "Invalid email or password."

            elif not user.check_password(password):

                error = "Invalid email or password."

            else:

                # Clear previous session
                session.clear()

                session["user_id"] = user.id
                session["user_name"] = user.name
                session["user_email"] = user.email
                session["user_role"] = user.role

                if user.role == "doctor":
                    session["doctor_id"] = user.doctor_id

                if user.role == "patient":
                    session["patient_id"] = user.patient_id

                return redirect_by_role(user)

        return render_template(
            "auth/login.html",
            error=error
        )

    # GET /web-login always shows login page
    return render_template(
        "auth/login.html",
        error=None
    )


@web_auth_bp.route("/web-logout")
def web_logout():

    session.clear()

    return redirect(
        url_for("web_auth.web_login")
    )


def web_admin_required(function):

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