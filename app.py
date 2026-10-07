from flask import Flask

from config import Config
from extensions import db, jwt


# ==================================================
# MODELS
# ==================================================

from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment


# ==================================================
# API BLUEPRINTS
# ==================================================

from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.appointment_routes import appointment_bp
from routes.api_routes import api_bp


# ==================================================
# WEB BLUEPRINTS
# ==================================================

from routes.analytics_routes import analytics_bp
from routes.web_auth import web_auth_bp
from routes.csv_routes import csv_bp
from routes.report_routes import report_bp

from routes.patient_web import patient_web_bp
from routes.doctor_web import doctor_web_bp

from routes.admin_patient_web import admin_patient_web_bp
from routes.admin_doctor_web import admin_doctor_web_bp
from routes.admin_appointment_web import admin_appointment_web_bp


# ==================================================
# CREATE APPLICATION
# ==================================================

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    jwt.init_app(app)


    # ==================================================
    # API ROUTES
    # ==================================================

    app.register_blueprint(auth_bp)

    app.register_blueprint(patient_bp)

    app.register_blueprint(doctor_bp)

    app.register_blueprint(appointment_bp)

    app.register_blueprint(api_bp)


    # ==================================================
    # ANALYTICS
    # ==================================================

    app.register_blueprint(
        analytics_bp
    )


    # ==================================================
    # ADMIN WEB AUTH
    # ==================================================

    app.register_blueprint(
        web_auth_bp
    )


    # ==================================================
    # CSV
    # ==================================================

    app.register_blueprint(
        csv_bp
    )


    # ==================================================
    # REPORTS
    # ==================================================

    app.register_blueprint(
        report_bp
    )


    # ==================================================
    # PATIENT WEB PORTAL
    # ==================================================

    app.register_blueprint(
        patient_web_bp
    )


    # ==================================================
    # DOCTOR WEB PORTAL
    # ==================================================

    app.register_blueprint(
        doctor_web_bp
    )


    # ==================================================
    # ADMIN PATIENT WEB
    # ==================================================

    app.register_blueprint(
        admin_patient_web_bp
    )


    # ==================================================
    # ADMIN DOCTOR WEB
    # ==================================================

    app.register_blueprint(
        admin_doctor_web_bp
    )


    # ==================================================
    # ADMIN APPOINTMENT WEB
    # ==================================================

    app.register_blueprint(
        admin_appointment_web_bp
    )


    # ==================================================
    # DATABASE
    # ==================================================

    with app.app_context():

        db.create_all()


    # ==================================================
    # HOME
    # ==================================================

    @app.route("/")
    def home():

        return {
            "message": (
                "Hospital Patient Record and "
                "Treatment Tracking System"
            ),
            "status": "running"
        }


    return app


# ==================================================
# APPLICATION INSTANCE
# ==================================================

app = create_app()


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )