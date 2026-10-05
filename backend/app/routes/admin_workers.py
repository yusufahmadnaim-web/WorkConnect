from flask import request
from flask_restful import Resource

from app.extensions import db
from app.models.worker import Worker
from app.utils.auth import roles_required


class PendingWorkersResource(Resource):
    @roles_required("admin")
    def get(self):
        workers = Worker.query.filter_by(
            verification_status="pending"
        ).all()

        return {
            "workers": [
                {
                    "id": worker.id,
                    "user_id": worker.user_id,
                    "full_name": worker.user.full_name,
                    "email": worker.user.email,
                    "bio": worker.bio,
                    "phone": worker.phone,
                    "location": worker.location,
                    "experience_years": worker.experience_years,
                    "hourly_rate": (
                        str(worker.hourly_rate)
                        if worker.hourly_rate is not None
                        else None
                    ),
                    "verification_status": worker.verification_status,
                    "categories": [
                        {
                            "id": category.id,
                            "name": category.name,
                        }
                        for category in worker.categories
                    ],
                }
                for worker in workers
            ]
        }, 200


class WorkerVerificationResource(Resource):
    @roles_required("admin")
    def patch(self, worker_id):
        data = request.get_json() or {}

        status = data.get("status")

        if status not in {"approved", "rejected"}:
            return {
                "message": "status must be either approved or rejected"
            }, 400

        worker = db.session.get(Worker, worker_id)

        if not worker:
            return {
                "message": "Worker not found"
            }, 404

        worker.verification_status = status

        db.session.commit()

        return {
            "message": f"Worker {status} successfully",
            "worker": {
                "id": worker.id,
                "user_id": worker.user_id,
                "full_name": worker.user.full_name,
                "verification_status": worker.verification_status,
            },
        }, 200