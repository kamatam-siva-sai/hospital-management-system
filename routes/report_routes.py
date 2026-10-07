from flask import Blueprint, send_file, redirect, url_for, flash

from routes.web_auth import web_admin_required
from services.report_generator import (
    generate_csv_report,
    generate_excel_report
)


report_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@report_bp.route("/csv", methods=["GET"])
@web_admin_required
def download_csv_report():

    try:
        file_path = generate_csv_report()

        return send_file(
            file_path,
            as_attachment=True,
            download_name="appointments_report.csv",
            mimetype="text/csv"
        )

    except Exception as error:

        flash(
            f"Unable to generate CSV report: {error}",
            "error"
        )

        return redirect(
            url_for("analytics.analytics_dashboard")
        )


@report_bp.route("/excel", methods=["GET"])
@web_admin_required
def download_excel_report():

    try:
        file_path = generate_excel_report()

        return send_file(
            file_path,
            as_attachment=True,
            download_name="hospital_report.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as error:

        flash(
            f"Unable to generate Excel report: {error}",
            "error"
        )

        return redirect(
            url_for("analytics.analytics_dashboard")
        )