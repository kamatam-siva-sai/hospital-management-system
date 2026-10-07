from app import app
from extensions import db
from models.user import User
from models.doctor import Doctor


with app.app_context():

    doctor = Doctor.query.get(1)

    if not doctor:
        print("Doctor ID 1 not found.")
        exit()

    existing_user = User.query.filter_by(
        email="ravi@hospital.com"
    ).first()

    if existing_user:
        print("Doctor account already exists.")

        existing_user.doctor_id = doctor.id
        existing_user.role = "doctor"
        existing_user.name = doctor.name

        db.session.commit()

        print("Doctor account linked successfully.")
        print("Name:", existing_user.name)
        print("Email:", existing_user.email)
        print("Password: ravi123")
        print("Doctor ID:", existing_user.doctor_id)

    else:
        doctor_user = User(
            name=doctor.name,
            email="ravi@hospital.com",
            role="doctor",
            doctor_id=doctor.id
        )

        doctor_user.set_password("ravi123")

        db.session.add(doctor_user)
        db.session.commit()

        print("Doctor account created successfully.")
        print("Name:", doctor_user.name)
        print("Email:", doctor_user.email)
        print("Password: ravi123")
        print("Role:", doctor_user.role)
        print("Doctor ID:", doctor_user.doctor_id)