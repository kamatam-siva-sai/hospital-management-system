import pandas as pd
import numpy as np

from models.appointment import Appointment


def get_appointments_dataframe():
    """
    Fetch appointments from MySQL and convert them
    into a Pandas DataFrame.
    """

    appointments = Appointment.query.all()

    data = []

    for appointment in appointments:
        data.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "date": appointment.date,
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        })

    if not data:
        return pd.DataFrame(
            columns=[
                "id",
                "patient_id",
                "patient_name",
                "doctor_id",
                "doctor_name",
                "date",
                "diagnosis",
                "status"
            ]
        )

    df = pd.DataFrame(data)

    df["date"] = pd.to_datetime(df["date"])

    return df


# ============================================================
# 1. COMMON DIAGNOSES
# ============================================================

def get_common_diagnoses():
    df = get_appointments_dataframe()

    if df.empty:
        return []

    result = (
        df["diagnosis"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "diagnosis",
        "appointment_count"
    ]

    return result.to_dict(orient="records")


# ============================================================
# 2. APPOINTMENT STATUS DISTRIBUTION
# ============================================================

def get_status_distribution():
    df = get_appointments_dataframe()

    if df.empty:
        return []

    result = (
        df["status"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "status",
        "appointment_count"
    ]

    return result.to_dict(orient="records")


# ============================================================
# 3. DOCTOR PERFORMANCE
# ============================================================

def get_doctor_performance():
    df = get_appointments_dataframe()

    if df.empty:
        return []

    result = (
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
                lambda x: (x == "Completed").sum()
            )
        )
        .reset_index()
    )

    result["recovery_rate"] = (
        result["completed_appointments"]
        / result["total_appointments"]
        * 100
    ).round(2)

    return result.to_dict(orient="records")


# ============================================================
# 4. AVERAGE RECOVERY TIME
# ============================================================

def get_average_recovery_time():
    """
    Calculates recovery time using appointment dates.

    For diagnoses with multiple appointments:
    recovery time = latest date - earliest date.
    """

    df = get_appointments_dataframe()

    if df.empty:
        return []

    result = (
        df.groupby(
            ["patient_id", "patient_name", "diagnosis"]
        )["date"]
        .agg(
            start_date="min",
            end_date="max"
        )
        .reset_index()
    )

    result["recovery_days"] = (
        result["end_date"] -
        result["start_date"]
    ).dt.days

    average_result = (
        result.groupby("diagnosis")["recovery_days"]
        .mean()
        .round(2)
        .reset_index()
    )

    average_result.columns = [
        "diagnosis",
        "average_recovery_days"
    ]

    return average_result.to_dict(
        orient="records"
    )


# ============================================================
# 5. TIME-SERIES APPOINTMENT TRENDS
# ============================================================

def get_appointment_trends():
    df = get_appointments_dataframe()

    if df.empty:
        return []

    result = (
        df.groupby(
            df["date"].dt.to_period("M")
        )
        .size()
        .reset_index(
            name="appointment_count"
        )
    )

    result["month"] = (
        result["date"]
        .astype(str)
    )

    result = result[
        [
            "month",
            "appointment_count"
        ]
    ]

    return result.to_dict(
        orient="records"
    )


# ============================================================
# 6. NUMPY STATISTICS
# ============================================================

def get_numpy_statistics():
    df = get_appointments_dataframe()

    if df.empty:
        return {
            "total_appointments": 0,
            "mean_appointments_per_day": 0,
            "median_appointments_per_day": 0,
            "standard_deviation": 0
        }

    daily_counts = (
        df.groupby(
            df["date"].dt.date
        )
        .size()
        .values
    )

    numpy_array = np.array(
        daily_counts,
        dtype=float
    )

    return {
        "total_appointments": int(
            np.sum(numpy_array)
        ),
        "mean_appointments_per_day": round(
            float(np.mean(numpy_array)),
            2
        ),
        "median_appointments_per_day": round(
            float(np.median(numpy_array)),
            2
        ),
        "standard_deviation": round(
            float(np.std(numpy_array)),
            2
        )
    }


# ============================================================
# 7. COMPLETE ANALYTICS
# ============================================================

def get_all_analytics():
    return {
        "common_diagnoses": get_common_diagnoses(),
        "status_distribution": get_status_distribution(),
        "doctor_performance": get_doctor_performance(),
        "average_recovery_time": get_average_recovery_time(),
        "appointment_trends": get_appointment_trends(),
        "numpy_statistics": get_numpy_statistics()
    }