from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from app.extensions import db
from app.models.booking import Booking
from app.models.worker import Worker
from app.utils.auth import roles_required


class BookingListResource(Resource):
    @roles_required("customer")
    def post(self):
        data = request.get_json() or {}

        worker_id = data.get("worker_id")
        service_description = data.get("service_description")
        scheduled_at = data.get("scheduled_at")
        agreed_price = data.get("agreed_price")

        if not worker_id or not service_description or not scheduled_at:
            return {
                "message": (
                    "worker_id, service_description and "
                    "scheduled_at are required"
                )
            }, 400

        worker = db.session.get(Worker, worker_id)

        if not worker:
            return {
                "message": "Worker not found"
            }, 404

        if worker.verification_status != "approved":
            return {
                "message": "This worker is not available for booking"
            }, 400

        customer_id = int(get_jwt_identity())

        booking = Booking(
            customer_id=customer_id,
            worker_id=worker.id,
            service_description=service_description.strip(),
            scheduled_at=scheduled_at,
            agreed_price=agreed_price,
        )

        db.session.add(booking)
        db.session.commit()

        return {
            "message": "Booking created successfully",
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "worker_id": booking.worker_id,
                "worker_name": worker.user.full_name,
                "service_description": booking.service_description,
                "scheduled_at": booking.scheduled_at.isoformat(),
                "agreed_price": (
                    str(booking.agreed_price)
                    if booking.agreed_price is not None
                    else None
                ),
                "status": booking.status,
            },
        }, 201

    @roles_required("customer")
    def get(self):
        customer_id = int(get_jwt_identity())

        bookings = Booking.query.filter_by(
            customer_id=customer_id
        ).order_by(
            Booking.created_at.desc()
        ).all()

        return {
            "bookings": [
                {
                    "id": booking.id,
                    "worker_id": booking.worker_id,
                    "worker_name": booking.worker.user.full_name,
                    "service_description": booking.service_description,
                    "scheduled_at": booking.scheduled_at.isoformat(),
                    "agreed_price": (
                        str(booking.agreed_price)
                        if booking.agreed_price is not None
                        else None
                    ),
                    "status": booking.status,
                    "created_at": booking.created_at.isoformat(),
                }
                for booking in bookings
            ]
        }, 200