from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from app.extensions import db
from app.models.category import Category
from app.models.worker_category import WorkerCategory
from app.models.worker import Worker
from app.utils.auth import roles_required


class CategoryListResource(Resource):
    def get(self):
        categories = Category.query.order_by(Category.name.asc()).all()

        return {
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                }
                for category in categories
            ]
        }, 200

    @roles_required("admin")
    def post(self):
        data = request.get_json() or {}

        name = data.get("name")
        description = data.get("description")

        if not name:
            return {
                "message": "Category name is required"
            }, 400

        name = name.strip()

        existing_category = Category.query.filter_by(
            name=name
        ).first()

        if existing_category:
            return {
                "message": "Category already exists"
            }, 409

        category = Category(
            name=name,
            description=description,
        )

        db.session.add(category)
        db.session.commit()

        return {
            "message": "Category created successfully",
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
            },
        }, 201


class WorkerCategoriesResource(Resource):
    @roles_required("worker")
    def post(self):
        data = request.get_json() or {}

        category_ids = data.get("category_ids")

        if not isinstance(category_ids, list) or not category_ids:
            return {
                "message": "category_ids must be a non-empty list"
            }, 400

        worker_id = int(get_jwt_identity())

        worker = Worker.query.filter_by(
            user_id=worker_id
        ).first()

        if not worker:
            return {
                "message": "Worker profile not found"
            }, 404

        categories = Category.query.filter(
            Category.id.in_(category_ids)
        ).all()

        if len(categories) != len(set(category_ids)):
            return {
                "message": "One or more categories do not exist"
            }, 404

        WorkerCategory.query.filter_by(
            worker_id=worker.id
        ).delete()

        for category in categories:
            worker_category = WorkerCategory(
                worker_id=worker.id,
                category_id=category.id,
            )

            db.session.add(worker_category)

        db.session.commit()

        return {
            "message": "Worker categories updated successfully",
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                }
                for category in categories
            ],
        }, 200