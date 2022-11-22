#!/usr/bin/python3
"""This module defines views for place object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.place import Place
from models.user import User
from models.city import City
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def places(city_id):
    """Retrieves the list of all place objects"""
    city = storage.get(City, city_id)
    if not city:
        abort(404, jsonify({"error": "Not found"}))

    if request.method == 'GET':
        return jsonify([place.to_dict() for place in city.places])


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def places_post(city_id):
    """creates a new place object"""
    city = storage.get(City, city_id)
    if not city:
        abort(404, jsonify({"error": "Not found"}))
    if not request.json:
        abort(400, jsonify({"error": "Not a JSON"}))
    new_place = request.get_json()
    if not new_place:
        abort(400, jsonify({"error": "Not a JSON"}))
    if "user_id" not in new_place:
        abort(400, jsonify({"error": "Missing user_id"}))
    user_id = new_place['user_id']
    if not storage.get(User, user_id):
        abort(404)
    if "name" not in new_place:
        abort(400, jsonify({"error": "Missing name"}))
    place = Place(**new_place)
    setattr(place, 'city_id', city_id)
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


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def places_search():
    """ Retrieves a JSON list of `Place` instances corresponding to lists of
    ids included in the body of the request.
    JSON request body can contain 3 optional keys:
        "states": list of `State` uuids
            adds each `Place` for each `City` for each `State` to list
        "cities": list of `City` uuids
            lists each `Place` for each `City` to list
        "amenities": list of `Amenity` uuids
            filters `Place` list by only those that have all listed amenities
        If entire request dict is empty, or both "state" and "city" are missing
    or empty, all `Place` instances in storage are added to list, before
    filtering by amenity.
    Return:
        JSON list of `Place` instances, status 200, or status 400 for invalid
    JSON
    """
    if request.is_json:
        req_dict = request.get_json()
    else:
        return (jsonify({'error': 'Not a JSON'}), 400)

    # complile list of all cities for named states + individually named cities
    city_list = []
    if 'states' in req_dict:
        for state_id in req_dict['states']:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    city_list.append(city)

    if 'cities' in req_dict:
        for city_id in req_dict['cities']:
            city = storage.get(City, city_id)
            if city:
                if city not in city_list:
                    city_list.append(city)

    # list all places to be found in those cities
    place_list = []
    for city in city_list:
        for place in city.places:
            place_list.append(place)

    # if no states or cities with valid ids provided, defaults to all places
    if len(place_list) == 0:
        for place in storage.all(Place).values():
            place_list.append(place)

    # filter places to only include those that share all listed amenities
    amenity_list = []
    if 'amenities' in req_dict:
        for amenity_id in req_dict['amenities']:
            amenity = storage.get(Amenity, amenity_id)
            if amenity:
                amenity_list.append(amenity)

        filtered_place_list = place_list.copy()
        for place in place_list:
            if not all(amenity in place.amenities for amenity in amenity_list):
                filtered_place_list.remove(place)
        place_list = filtered_place_list

    # prepare return list
    place_dict_list = []
    for place in place_list:
        place_dict = place.to_dict()
        if 'amenities' in place_dict:
            del place_dict['amenities']
        place_dict_list.append(place_dict)

    return jsonify(place_dict_list)
    # """
    # Retrieves all Place objects depending of
    # the JSON in the body of the request
    # """
    # body_r = request.get_json()
    # if body_r is None:
    #     abort(400, jsonify({"error": "Not a JSON"}))

    # if not body_r or (
    #         not body_r.get('states') and
    #         not body_r.get('cities') and
    #         not body_r.get('amenities')
    # ):
    #     places = storage.all(Place)
    #     return jsonify([place.to_dict() for place in places.values()])

    # places = []

    # if body_r.get('states'):
    #     states = [storage.get(State, id) for id in body_r['states']]

    #     for state in states:
    #         for city in state.cities:
    #             for place in city.places:
    #                 places.append(place)

    # if body_r.get('cities'):
    #     cities = [storage.get(City, id) for id in body_r.get('cities')]

    #     for city in cities:
    #         for place in city.places:
    #             if place not in places:
    #                 places.append(place)

    # if not places:
    #     places = storage.all(Place)
    #     places = [place for place in places.values()]

    # if body_r.get('amenities'):
    #     ams = [storage.get(Amenity, id) for id in body_r.get('amenities')]
    #     i = 0
    #     limit = len(places)
    #     HBNB_API_HOST = getenv('HBNB_API_HOST')
    #     HBNB_API_PORT = getenv('HBNB_API_PORT')

    #     port = 5000 if not HBNB_API_PORT else HBNB_API_PORT
    #     first_url = "http://0.0.0.0:{}/api/v1/places/".format(port)
    #     while i < limit:
    #         place = places[i]
    #         url = first_url + '{}/amenities'
    #         req = url.format(place.id)
    #         response = requests.get(req)
    #         am_d = json.loads(response.text)
    #         amenities = [storage.get(Amenity, o['id']) for o in am_d]
    #         for amenity in ams:
    #             if amenity not in amenities:
    #                 places.pop(i)
    #                 i -= 1
    #                 limit -= 1
    #                 break
    #         i += 1
    # return jsonify([place.to_dict() for place in places])
