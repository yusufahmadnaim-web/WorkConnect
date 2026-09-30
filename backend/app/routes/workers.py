from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from app.extensions import db
from app.models.worker import Worker
from app.models.category import Category
from app.utils.auth import roles_required


class WorkerProfileResource(Resource):
    @roles_required("worker")
    def post(self):
        data = request.get_json() or {}

        user_id = int(get_jwt_identity())

        existing_profile = Worker.query.filter_by(
            user_id=user_id
        ).first()

        if existing_profile:
            return {
                "message": "Worker profile already exists"
            }, 409

        worker = Worker(
            user_id=user_id,
            bio=data.get("bio"),
            phone=data.get("phone"),
            location=data.get("location"),
            experience_years=data.get("experience_years"),
            hourly_rate=data.get("hourly_rate"),
        )

        db.session.add(worker)
        db.session.commit()

        return {
            "message": "Worker profile created successfully",
            "worker": {
                "id": worker.id,
                "user_id": worker.user_id,
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
            },
        }, 201

    @roles_required("worker")
    def get(self):
        user_id = int(get_jwt_identity())

        worker = Worker.query.filter_by(
            user_id=user_id
        ).first()

        if not worker:
            return {
                "message": "Worker profile not found"
            }, 404

        return {
            "worker": {
                "id": worker.id,
                "user_id": worker.user_id,
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
            }
        }, 200


class WorkerListResource(Resource):
    def get(self):
        category_name = request.args.get("category")
        location = request.args.get("location")

        query = Worker.query.filter_by(
            verification_status="approved"
        )

        if category_name:
            query = query.join(Worker.categories).filter(
                db.func.lower(Category.name) == category_name.strip().lower()
            )

        if location:
            query = query.filter(
                Worker.location.ilike(f"%{location.strip()}%")
            )

        workers = query.all()

        return {
            "workers": [
                {
                    "id": worker.id,
                    "user_id": worker.user_id,
                    "full_name": worker.user.full_name,
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