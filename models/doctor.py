from extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    appointments = db.relationship(
        "Appointment",
        backref="doctor",
        lazy=True
    )

    def __repr__(self):
        return f"<Doctor {self.name}>"