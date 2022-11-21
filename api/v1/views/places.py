#!/usr/bin/python3
"""This module defines views for place object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.place import Place
from models.user import User
from models.city import City


@app_views.route('/cities/<city_id>/places',
                 methods=['GET', 'POST'], strict_slashes=False)
def places(city_id):
    """Retrieves the list of all place objects"""
    city = storage.get(City, city_id)
    if not city:
        abort(404, jsonify({"error": "Not found"}))

    if request.method == 'GET':
        return jsonify([place.to_dict() for place in city.places])

    elif request.method == 'POST':
        if not request.json:
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        if "user_id" not in details:
            abort(400, jsonify({"error": "Missing user_id"}))
        user_id = details["user_id"]
        user = storage.get(User, user_id)
        if "name" not in details:
            abort(400, jsonify({"error": "Missing name"}))
        place = Place(name=details["name"], city_id=city_id, user_id=user_id)
        for k, v in details.items():
            setattr(place, k, v)
        storage.new(place)
        storage.save()
        return make_response(jsonify(place.to_dict()), 201)


@app_views.route('places/<place_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def place_id(place_id):
    """Retrieves a place object by its id"""
    place = storage.get(Place, place_id)
    if place is not None:
        if request.method == 'GET':
            return jsonify(place.to_dict())

        if request.method == 'DELETE':
            place.delete()
            storage.save()
            return make_response(jsonify({}), 200)

        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "user_id",
                         "city_id", "created_at",
                         "updated_at", "place_id"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(place, k, v)
            storage.save()
            return make_response(jsonify(place.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))
