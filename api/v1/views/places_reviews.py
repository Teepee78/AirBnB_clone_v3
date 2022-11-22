#!/usr/bin/python3
"""This module defines views for Review object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.review import Review
from models.place import Place
from models.user import User


@app_views.route('/places/<place_id>/reviews',
                 methods=['GET'], strict_slashes=False)
def review(place_id):
    """Retrieves the list of all reviews for a place objects"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404, jsonify({"error": "Not found"}))

    return jsonify([review.to_dict() for review in place.reviews])


@app_views.route('/places/<place_id>/reviews',
                 methods=['POST'], strict_slashes=False)
def review_post(place_id):
    """creates a new review object """
    place = storage.get(Place, place_id)
    if not place:
        abort(404, jsonify({"error": "Not found"}))
    details = request.get_json()
    if not details:
        abort(400, jsonify({"error": "Not a JSON"}))

    if "user_id" not in details:
        abort(400, jsonify({"error": "Missing user_id"}))

    user_id = details["user_id"]
    if not storage.get(User, user_id):
        abort(404, jsonify({"error": "Not found"}))
    if "text" not in details:
        abort(400, jsonify({"error": "Missing text"}))
    review = Review(**details)
    setattr(review, 'place_id', place_id)
    storage.new(review)
    storage.save()
    return make_response(jsonify(review.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE'],
                 strict_slashes=False)
def handle_review(review_id):
    """Handles basic method of the reviews endpoint"""
    review = storage.get(Review, review_id)
    if not review:
        return abort(404, jsonify({"error": "Not found"}))

    # if request method is GET
    if request.method == 'GET':
        return jsonify(review.to_dict())

    # if request method is Delete, delete review
    if request.method == 'DELETE':
        review.delete()
        storage.save()
        return make_response(jsonify({}), 200)


@app_views.route('/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """Handles update method of the reviews endpoint"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    updates = request.get_json(silent=True)
    if not updates:
        return jsonify(error="Not a JSON"), 400

    updates.pop("id", None)
    updates.pop("user_id", None)
    updates.pop("place_id", None)
    updates.pop("created_at", None)
    updates.pop("updated_at", None)

    for k, v in updates.items():
        setattr(review, k, v)
    review.save()
    return jsonify(review.to_dict()), 200
