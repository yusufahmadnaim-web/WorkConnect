

from datetime import datetime

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from app.extensions import db
from app.models.worker import Worker
from app.models.worker_availability import WorkerAvailability
from app.utils.auth import roles_required


class WorkerAvailabilityResource(Resource):

    def get_worker(self):
        user_id = int(get_jwt_identity())

        return Worker.query.filter_by(
            user_id=user_id
        ).first()

    def serialize_availability(self, item):
        return {
            "id": item.id,
            "day_of_week": item.day_of_week,
            "start_time": item.start_time.strftime("%H:%M"),
            "end_time": item.end_time.strftime("%H:%M"),
            "is_available": item.is_available,
        }

    @roles_required("worker")
    def get(self):
        worker = self.get_worker()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        availability = WorkerAvailability.query.filter_by(
            worker_id=worker.id
        ).order_by(
            WorkerAvailability.day_of_week
        ).all()

        return {
            "availability": [
                self.serialize_availability(item)
                for item in availability
            ]
        }, 200

    @roles_required("worker")
    def post(self):
        worker = self.get_worker()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return {"message": "A valid JSON object is required"}, 400

        day_of_week = data.get("day_of_week")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        is_available = data.get("is_available", True)

        if day_of_week is None or not start_time or not end_time:
            return {
                "message": "day_of_week, start_time and end_time are required"
            }, 400

        if type(day_of_week) is not int or not 0 <= day_of_week <= 6:
            return {
                "message": "day_of_week must be an integer between 0 and 6"
            }, 400

        if type(is_available) is not bool:
            return {"message": "is_available must be a boolean"}, 400

        if not isinstance(start_time, str) or not isinstance(end_time, str):
            return {"message": "Times must use HH:MM format"}, 400

        existing = WorkerAvailability.query.filter_by(
            worker_id=worker.id,
            day_of_week=day_of_week
        ).first()

        if existing:
            return {
                "message": "Availability for this day already exists"
            }, 409

        try:
            parsed_start = datetime.strptime(start_time, "%H:%M").time()
            parsed_end = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            return {"message": "Times must use HH:MM format"}, 400

        if parsed_start >= parsed_end:
            return {
                "message": "start_time must be earlier than end_time"
            }, 400

        availability = WorkerAvailability(
            worker_id=worker.id,
            day_of_week=day_of_week,
            start_time=parsed_start,
            end_time=parsed_end,
            is_available=is_available
        )

        try:
            db.session.add(availability)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"message": "Could not create availability"}, 500

        return {
            "message": "Availability created successfully",
            "availability": self.serialize_availability(availability)
        }, 201

    @roles_required("worker")
    def put(self, availability_id):
        worker = self.get_worker()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        availability = WorkerAvailability.query.filter_by(
            id=availability_id,
            worker_id=worker.id
        ).first()

        if not availability:
            return {"message": "Availability record not found"}, 404

        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return {"message": "A valid JSON object is required"}, 400

        day_of_week = data.get(
            "day_of_week",
            availability.day_of_week
        )
        start_time = data.get(
            "start_time",
            availability.start_time.strftime("%H:%M")
        )
        end_time = data.get(
            "end_time",
            availability.end_time.strftime("%H:%M")
        )
        is_available = data.get(
            "is_available",
            availability.is_available
        )

        if type(day_of_week) is not int or not 0 <= day_of_week <= 6:
            return {
                "message": "day_of_week must be an integer between 0 and 6"
            }, 400

        if type(is_available) is not bool:
            return {"message": "is_available must be a boolean"}, 400

        if not isinstance(start_time, str) or not isinstance(end_time, str):
            return {"message": "Times must use HH:MM format"}, 400

        try:
            parsed_start = datetime.strptime(start_time, "%H:%M").time()
            parsed_end = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            return {"message": "Times must use HH:MM format"}, 400

        if parsed_start >= parsed_end:
            return {
                "message": "start_time must be earlier than end_time"
            }, 400

        duplicate = WorkerAvailability.query.filter(
            WorkerAvailability.worker_id == worker.id,
            WorkerAvailability.day_of_week == day_of_week,
            WorkerAvailability.id != availability.id
        ).first()

        if duplicate:
            return {
                "message": "Availability for this day already exists"
            }, 409

        availability.day_of_week = day_of_week
        availability.start_time = parsed_start
        availability.end_time = parsed_end
        availability.is_available = is_available

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"message": "Could not update availability"}, 500

        return {
            "message": "Availability updated successfully",
            "availability": self.serialize_availability(availability)
        }, 200

    @roles_required("worker")
    def delete(self, availability_id):
        worker = self.get_worker()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        availability = WorkerAvailability.query.filter_by(
            id=availability_id,
            worker_id=worker.id
        ).first()

        if not availability:
            return {"message": "Availability record not found"}, 404

        try:
            db.session.delete(availability)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"message": "Could not delete availability"}, 500

        return {
            "message": "Availability deleted successfully"
        }, 200
