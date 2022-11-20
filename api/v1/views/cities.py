#!/usr/bin/python3
"""This module defines views for city object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.city import City


@app_views.route('/states/<uuid:state_id>/cities',
                 methods=['GET', 'POST'], strict_slashes=False)
def cities(state_id):
    """Retrieves the list of all city objects"""
    all_cities = storage.all(City)
    cities = []

    for city in all_cities.values():
        if city.state_id == state_id:
            cities.append(city.to_dict())

    if request.method == 'GET':
        if len(cities) > 0:
            return jsonify(cities)
        abort(404, jsonify({"error": "Not found"}))

    elif request.method == 'POST':
        if not cities:
            abort(404, jsonify({"error": "Not found"}))
        if not request.json:
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        if "name" in details:
            name = details["name"]
            city = City(name=name)
            for k, v in details.items():
                setattr(city, k, v)
            city.save()
            return make_response(jsonify(city.to_dict()), 201)
        abort(400, jsonify({"error": "Missing name"}))


@app_views.route('cities/<uuid:city_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def city_id(state_id):
    """Retrieves a city object by its id"""
    city = storage.get(City, city_id)
    if city is not None:
        if request.method == 'GET':
            return jsonify(city.to_dict())

        if request.method == 'DELETE':
            city.delete()
            storage.save()
            return make_response(jsonify({}), 200)

        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "created_at", "updated_at"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(city, k, v)
            city.save()
            return make_response(jsonify(city.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))
