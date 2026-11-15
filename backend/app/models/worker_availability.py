from app.extensions import db


class WorkerAvailability(db.Model):
    __tablename__ = "worker_availabilities"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("workers.id"),
        nullable=False,
    )

    day_of_week = db.Column(
        db.Integer,
        nullable=False,
    )

    start_time = db.Column(
        db.Time,
        nullable=False,
    )

    end_time = db.Column(
        db.Time,
        nullable=False,
    )

    is_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    worker = db.relationship(
        "Worker",
        backref=db.backref(
            "availability",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "worker_id",
            "day_of_week",
            name="uq_worker_availability_day",
        ),
        db.CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_worker_availability_day_range",
        ),
        db.CheckConstraint(
            "start_time < end_time",
            name="ck_worker_availability_time_range",
        ),
    )

    def __repr__(self):
        return (
            f"<WorkerAvailability worker_id={self.worker_id} "
            f"day={self.day_of_week}>"
        )
