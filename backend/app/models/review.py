from datetime import datetime, timezone

from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False,
        unique=True,
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

    rating = db.Column(
        db.Integer,
        nullable=False,
    )

    comment = db.Column(
        db.Text,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    booking = db.relationship("Booking", backref="review")

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        backref=db.backref("reviews_written", lazy=True),
    )

    worker = db.relationship(
        "Worker",
        foreign_keys=[worker_id],
        backref=db.backref("reviews_received", lazy=True),
    )

    def __repr__(self):
        return (
            f"<Review booking_id={self.booking_id} "
            f"rating={self.rating}>"
        )
