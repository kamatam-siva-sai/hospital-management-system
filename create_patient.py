from app import app
from extensions import db
from models.user import User
from models.patient import Patient


with app.app_context():

    # Find existing patient
    patient = Patient.query.get(2)

    if not patient:
        print("Patient ID 2 not found.")
        exit()

    # Check whether account already exists
    existing_user = User.query.filter_by(
        email="patient@hospital.com"
    ).first()

    if existing_user:
        print("Patient account already exists.")
        print("Email: patient@hospital.com")
        print("Password: patient123")
        print(f"Patient ID: {existing_user.patient_id}")

    else:
        user = User(
            name=patient.name,
            email="patient@hospital.com",
            role="patient",
            patient_id=patient.id
        )

        user.set_password("patient123")

        db.session.add(user)
        db.session.commit()

        print("Patient account created successfully.")
        print("Name:", patient.name)
        print("Email: patient@hospital.com")
        print("Password: patient123")
        print("Patient ID:", patient.id)