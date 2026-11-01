from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from app.extensions import db
from app.models.booking import Booking
from app.models.review import Review
from app.utils.auth import roles_required


class CustomerReviewResource(Resource):
    @roles_required("customer")
    def post(self, booking_id):
        customer_id = int(get_jwt_identity())
        data = request.get_json() or {}

        rating = data.get("rating")
        comment = data.get("comment")

        # Validate rating.
        if isinstance(rating, bool) or not isinstance(rating, int):
            return {"message": "rating must be an integer from 1 to 5"}, 400

        if not 1 <= rating <= 5:
            return {"message": "rating must be between 1 and 5"}, 400

        if comment is not None and not isinstance(comment, str):
            return {"message": "comment must be a string"}, 400

        booking = db.session.get(Booking, booking_id)

        # Only the customer who owns the booking can review it.
        if not booking or booking.customer_id != customer_id:
            return {"message": "Booking not found"}, 404

        # Reviews are allowed only after customer confirmation.
        if booking.status != "confirmed":
            return {
                "message": "Only confirmed bookings can be reviewed"
            }, 400

        # Each booking can receive only one review.
        existing_review = Review.query.filter_by(
            booking_id=booking.id
        ).first()

        if existing_review:
            return {
                "message": "This booking has already been reviewed"
            }, 409

        review = Review(
            booking_id=booking.id,
            customer_id=customer_id,
            worker_id=booking.worker_id,
            rating=rating,
            comment=comment.strip() if comment else None,
        )

        db.session.add(review)
        db.session.commit()

        return {
            "message": "Review submitted successfully",
            "review": {
                "id": review.id,
                "booking_id": review.booking_id,
                "worker_id": review.worker_id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat(),
            },
        }, 201
