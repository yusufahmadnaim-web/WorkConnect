from app.extensions import db


class WorkerCategory(db.Model):
    __tablename__ = "worker_categories"

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("workers.id"),
        primary_key=True,
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        primary_key=True,
    )