import os

import pandas as pd

from config import BASE_DIR
from services.analytics import get_appointments_dataframe


REPORT_CSV_FOLDER = BASE_DIR / "reports" / "csv"
REPORT_EXCEL_FOLDER = BASE_DIR / "reports" / "excel"

os.makedirs(REPORT_CSV_FOLDER, exist_ok=True)
os.makedirs(REPORT_EXCEL_FOLDER, exist_ok=True)


def generate_csv_report():
    """
    Generate a CSV report containing all appointments.
    """

    df = get_appointments_dataframe()

    file_path = REPORT_CSV_FOLDER / "appointments_report.csv"

    df.to_csv(
        file_path,
        index=False
    )

    return file_path


def generate_excel_report():
    """
    Generate an Excel report containing appointment data
    and analytics sheets.
    """

    df = get_appointments_dataframe()

    file_path = REPORT_EXCEL_FOLDER / "hospital_report.xlsx"

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        # Sheet 1: All appointments
        df.to_excel(
            writer,
            sheet_name="Appointments",
            index=False
        )

        # Sheet 2: Common diagnoses
        if not df.empty:
            common_diagnoses = (
                df["diagnosis"]
                .value_counts()
                .reset_index()
            )

            common_diagnoses.columns = [
                "Diagnosis",
                "Appointment Count"
            ]
        else:
            common_diagnoses = pd.DataFrame(
                columns=[
                    "Diagnosis",
                    "Appointment Count"
                ]
            )

        common_diagnoses.to_excel(
            writer,
            sheet_name="Common Diagnoses",
            index=False
        )

        # Sheet 3: Status distribution
        if not df.empty:
            status_distribution = (
                df["status"]
                .value_counts()
                .reset_index()
            )

            status_distribution.columns = [
                "Status",
                "Appointment Count"
            ]
        else:
            status_distribution = pd.DataFrame(
                columns=[
                    "Status",
                    "Appointment Count"
                ]
            )

        status_distribution.to_excel(
            writer,
            sheet_name="Status Distribution",
            index=False
        )

        # Sheet 4: Doctor performance
        if not df.empty:
            doctor_performance = (
                df.groupby(
                    ["doctor_id", "doctor_name"]
                )
                .agg(
                    patients_treated=(
                        "patient_id",
                        "nunique"
                    ),
                    total_appointments=(
                        "id",
                        "count"
                    ),
                    completed_appointments=(
                        "status",
                        lambda x: (
                            x == "Completed"
                        ).sum()
                    )
                )
                .reset_index()
            )

            doctor_performance[
                "recovery_rate"
            ] = (
                doctor_performance[
                    "completed_appointments"
                ]
                / doctor_performance[
                    "total_appointments"
                ]
                * 100
            ).round(2)

        else:
            doctor_performance = pd.DataFrame(
                columns=[
                    "doctor_id",
                    "doctor_name",
                    "patients_treated",
                    "total_appointments",
                    "completed_appointments",
                    "recovery_rate"
                ]
            )

        doctor_performance.to_excel(
            writer,
            sheet_name="Doctor Performance",
            index=False
        )

    return file_path