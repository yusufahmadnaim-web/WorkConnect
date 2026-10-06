from datetime import datetime, timezone

from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("workers.id"),
        nullable=False,
    )

    service_description = db.Column(
        db.Text,
        nullable=False,
    )

    scheduled_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )

    agreed_price = db.Column(
        db.Numeric(10, 2),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        backref=db.backref(
            "bookings",
            lazy=True,
        ),
    )

    worker = db.relationship(
        "Worker",
        foreign_keys=[worker_id],
        backref=db.backref(
            "bookings",
            lazy=True,
        ),
    )

    def __repr__(self):
        return (
            f"<Booking customer_id={self.customer_id} "
            f"worker_id={self.worker_id} "
            f"status={self.status}>"
        )