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


class WorkerBookingListResource(Resource):
    @roles_required("worker")
    def get(self):
        user_id = int(get_jwt_identity())

        worker = Worker.query.filter_by(
            user_id=user_id
        ).first()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        bookings = Booking.query.filter_by(
            worker_id=worker.id
        ).order_by(
            Booking.created_at.desc()
        ).all()

        return {
            "bookings": [
                {
                    "id": booking.id,
                    "customer_id": booking.customer_id,
                    "customer_name": booking.customer.full_name,
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


class WorkerBookingStatusResource(Resource):
    @roles_required("worker")
    def patch(self, booking_id):
        data = request.get_json() or {}
        status = data.get("status")

        if status not in {"accepted", "rejected"}:
            return {
                "message": "status must be accepted or rejected"
            }, 400

        user_id = int(get_jwt_identity())

        worker = Worker.query.filter_by(
            user_id=user_id
        ).first()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        booking = db.session.get(Booking, booking_id)

        if not booking or booking.worker_id != worker.id:
            return {"message": "Booking not found"}, 404

        if booking.status != "pending":
            return {
                "message": "Only pending bookings can be updated"
            }, 400

        booking.status = status
        db.session.commit()

        return {
            "message": f"Booking {status} successfully",
            "booking": {
                "id": booking.id,
                "status": booking.status,
            },
        }, 200

class CustomerBookingCancelResource(Resource):
    @roles_required("customer")
    def delete(self, booking_id):
        customer_id = int(get_jwt_identity())

        booking = db.session.get(Booking, booking_id)

        # Customers can only access their own bookings.
        if not booking or booking.customer_id != customer_id:
            return {"message": "Booking not found"}, 404

        # Only pending bookings can be cancelled.
        if booking.status != "pending":
            return {
                "message": "Only pending bookings can be cancelled"
            }, 400

        booking.status = "cancelled"
        db.session.commit()

        return {
            "message": "Booking cancelled successfully",
            "booking": {
                "id": booking.id,
                "status": booking.status,
            },
        }, 200
class CustomerBookingDetailResource(Resource):
    @roles_required("customer")
    def get(self, booking_id):
        customer_id = int(get_jwt_identity())

        booking = db.session.get(Booking, booking_id)

        if not booking or booking.customer_id != customer_id:
            return {"message": "Booking not found"}, 404

        return {
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
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
        }, 200


class WorkerBookingDetailResource(Resource):
    @roles_required("worker")
    def get(self, booking_id):
        user_id = int(get_jwt_identity())

        worker = Worker.query.filter_by(user_id=user_id).first()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        booking = db.session.get(Booking, booking_id)

        if not booking or booking.worker_id != worker.id:
            return {"message": "Booking not found"}, 404

        return {
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "customer_name": booking.customer.full_name,
                "worker_id": booking.worker_id,
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
        }, 200

class WorkerBookingCompleteResource(Resource):
    @roles_required("worker")
    def patch(self, booking_id):
        user_id = int(get_jwt_identity())

        worker = Worker.query.filter_by(
            user_id=user_id
        ).first()

        if not worker:
            return {"message": "Worker profile not found"}, 404

        booking = db.session.get(Booking, booking_id)

        if not booking or booking.worker_id != worker.id:
            return {"message": "Booking not found"}, 404

        if booking.status != "accepted":
            return {
                "message": "Only accepted bookings can be completed"
            }, 400

        booking.status = "completed"
        db.session.commit()

        return {
            "message": "Booking completed successfully",
            "booking": {
                "id": booking.id,
                "status": booking.status,
            },
        }, 200

class CustomerBookingConfirmResource(Resource):
    @roles_required("customer")
    def patch(self, booking_id):
        customer_id = int(get_jwt_identity())

        booking = db.session.get(Booking, booking_id)

        if not booking or booking.customer_id != customer_id:
            return {"message": "Booking not found"}, 404

        if booking.status != "completed":
            return {
                "message": "Only completed bookings can be confirmed"
            }, 400

        booking.status = "confirmed"
        db.session.commit()

        return {
            "message": "Booking confirmed successfully",
            "booking": {
                "id": booking.id,
                "status": booking.status,
            },
        }, 200
