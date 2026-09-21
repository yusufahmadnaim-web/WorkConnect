from datetime import datetime, timezone

from app.extensions import db


class Worker(db.Model):
    __tablename__ = "workers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    bio = db.Column(db.Text, nullable=True)

    phone = db.Column(db.String(30), nullable=True)

    location = db.Column(db.String(255), nullable=True)

    experience_years = db.Column(db.Integer, nullable=True)

    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True)

    verification_status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "worker_profile",
            uselist=False,
        ),
    )

    def __repr__(self):
        return f"<Worker user_id={self.user_id}>"


    categories = db.relationship(
    "Category",
    secondary="worker_categories",
    backref=db.backref(
        "workers",
        lazy="dynamic",
    ),
)