from flask import Blueprint, jsonify, render_template

from services.analytics import get_all_analytics
from routes.decorators import role_required
from routes.web_auth import web_admin_required


analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)


# ============================================================
# ANALYTICS JSON API
# ============================================================

@analytics_bp.route("/", methods=["GET"])
@role_required("admin")
def analytics_api():

    analytics = get_all_analytics()

    return jsonify({
        "message": "Hospital analytics generated successfully",
        "analytics": analytics
    }), 200


# ============================================================
# ANALYTICS WEB DASHBOARD
# ============================================================

@analytics_bp.route("/dashboard", methods=["GET"])
@web_admin_required
def analytics_dashboard():

    analytics = get_all_analytics()

    return render_template(
        "analytics/dashboard.html",

        common_diagnoses=analytics[
            "common_diagnoses"
        ],

        status_distribution=analytics[
            "status_distribution"
        ],

        doctor_performance=analytics[
            "doctor_performance"
        ],

        average_recovery_time=analytics[
            "average_recovery_time"
        ],

        appointment_trends=analytics[
            "appointment_trends"
        ],

        numpy_statistics=analytics[
            "numpy_statistics"
        ]
    )