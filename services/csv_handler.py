import pandas as pd
from datetime import datetime

from extensions import db
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor


REQUIRED_COLUMNS = [
    "patient_id",
    "doctor_id",
    "date",
    "diagnosis",
    "status"
]


def validate_csv_columns(df):
    """
    Check whether all required columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing_columns


def upload_appointments_from_csv(file_path):
    """
    Read appointment records from a CSV file,
    validate them, and insert valid records
    into MySQL.
    """

    try:
        df = pd.read_csv(file_path)

    except Exception as error:
        return {
            "success": False,
            "message": f"Unable to read CSV file: {error}",
            "inserted": 0,
            "errors": []
        }

    # Remove spaces from column names
    df.columns = [
        column.strip()
        for column in df.columns
    ]

    # Validate columns
    missing_columns = validate_csv_columns(df)

    if missing_columns:

        return {
            "success": False,
            "message": "Required columns are missing",
            "missing_columns": missing_columns,
            "inserted": 0,
            "errors": []
        }

    inserted = 0
    errors = []

    # Process each row
    for index, row in df.iterrows():

        row_number = index + 2

        try:

            # -----------------------------
            # Get values
            # -----------------------------

            patient_id = int(row["patient_id"])
            doctor_id = int(row["doctor_id"])

            date_string = str(
                row["date"]
            ).strip()

            diagnosis = str(
                row["diagnosis"]
            ).strip()

            status = str(
                row["status"]
            ).strip()

            # -----------------------------
            # Validate diagnosis
            # -----------------------------

            if not diagnosis:
                raise ValueError(
                    "Diagnosis cannot be empty"
                )

            # -----------------------------
            # Validate status
            # -----------------------------

            if not status:
                raise ValueError(
                    "Status cannot be empty"
                )

            # -----------------------------
            # Validate patient
            # -----------------------------

            patient = Patient.query.get(
                patient_id
            )

            if not patient:
                raise ValueError(
                    f"Patient ID {patient_id} not found"
                )

            # -----------------------------
            # Validate doctor
            # -----------------------------

            doctor = Doctor.query.get(
                doctor_id
            )

            if not doctor:
                raise ValueError(
                    f"Doctor ID {doctor_id} not found"
                )

            # -----------------------------
            # Validate date
            # -----------------------------

            try:

                appointment_date = datetime.strptime(
                    date_string,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                raise ValueError(
                    "Date must be in YYYY-MM-DD format"
                )

            # -----------------------------
            # Create appointment
            # -----------------------------

            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                date=appointment_date,
                diagnosis=diagnosis,
                status=status
            )

            db.session.add(appointment)

            inserted += 1

        except Exception as error:

            errors.append({
                "row": row_number,
                "error": str(error)
            })

    # Commit valid records
    try:

        db.session.commit()

    except Exception as error:

        db.session.rollback()

        return {
            "success": False,
            "message": f"Database error: {error}",
            "inserted": 0,
            "errors": errors
        }

    return {
        "success": True,
        "message": "CSV processed successfully",
        "inserted": inserted,
        "errors": errors
    }