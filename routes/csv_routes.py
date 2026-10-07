import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from werkzeug.utils import secure_filename

from config import BASE_DIR
from services.csv_handler import upload_appointments_from_csv
from routes.web_auth import web_admin_required


csv_bp = Blueprint(
    "csv",
    __name__,
    url_prefix="/csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_FOLDER = BASE_DIR / "uploads" / "appointments"

ALLOWED_EXTENSIONS = {
    "csv"
}


# Create upload directory if it doesn't exist
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


def allowed_file(filename):
    """
    Check whether uploaded file is a CSV file.
    """

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# CSV UPLOAD PAGE
# ============================================================

@csv_bp.route("/upload", methods=["GET"])
@web_admin_required
def upload_page():

    return render_template(
        "csv/upload.html"
    )


# ============================================================
# PROCESS CSV UPLOAD
# ============================================================

@csv_bp.route("/upload", methods=["POST"])
@web_admin_required
def upload_csv():

    # Check file
    if "file" not in request.files:

        flash(
            "No file selected.",
            "error"
        )

        return redirect(
            url_for("csv.upload_page")
        )

    file = request.files["file"]

    # Check filename
    if file.filename == "":

        flash(
            "Please select a CSV file.",
            "error"
        )

        return redirect(
            url_for("csv.upload_page")
        )

    # Check extension
    if not allowed_file(file.filename):

        flash(
            "Only CSV files are allowed.",
            "error"
        )

        return redirect(
            url_for("csv.upload_page")
        )

    # Secure filename
    filename = secure_filename(
        file.filename
    )

    file_path = UPLOAD_FOLDER / filename

    # Save uploaded file
    file.save(file_path)

    # Process CSV
    result = upload_appointments_from_csv(
        file_path
    )

    # -----------------------------
    # Success
    # -----------------------------

    if result["success"]:

        message = (
            f"CSV uploaded successfully. "
            f"{result['inserted']} appointment(s) inserted."
        )

        flash(
            message,
            "success"
        )

    # -----------------------------
    # Failure
    # -----------------------------

    else:

        flash(
            result["message"],
            "error"
        )

    # -----------------------------
    # Row errors
    # -----------------------------

    if result.get("errors"):

        for error in result["errors"]:

            flash(
                f"Row {error['row']}: "
                f"{error['error']}",
                "error"
            )

    # -----------------------------
    # Missing columns
    # -----------------------------

    if result.get("missing_columns"):

        flash(
            "Missing columns: "
            + ", ".join(
                result["missing_columns"]
            ),
            "error"
        )

    return redirect(
        url_for("csv.upload_page")
    )