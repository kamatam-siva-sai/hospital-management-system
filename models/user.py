from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="doctor"
    )

    # Connect doctor account to Doctor record
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=True
    )

    # Connect patient account to Patient record
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=True
    )

    doctor = db.relationship(
        "Doctor",
        backref="user",
        uselist=False
    )

    patient = db.relationship(
        "Patient",
        backref="user",
        uselist=False
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password,
            password
        )

    def __repr__(self):
        return f"<User {self.email}>"