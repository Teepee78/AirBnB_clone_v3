#!/usr/bin/python3
""" View for place and Amentity objects """
from api.v1.views import app_views
from flask import jsonify, make_response, request, abort
from models import storage
from models.place import Place
from models.amenity import Amenity
from os import getenv


@app_views.route('/places/<place_id>/amenities', methods=['GET'],
                 strict_slashes=False)
def places_amenities(place_id):
    """Retrieves list of Amenities in a place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        a_list = [amenity.to_dict() for amentity in place.amenities]
        return a_list
    else:
        return jsonify([storage.get(Amentity, a_id).to_dict()
                        for a_id in place.amenities])


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'], strict_slashes=False)
def del_places_amenities(place_id, amenity_id):
    """ Deletes an Amenity object """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        if amenity not in place.amenities:
            abort(404)
    else:
        if amenity_id not in place.amenity_ids:
            abort(404, jsonify({"error": "Not found"}))
        index = place.amenity_ids.index(amenity_id)
        place.amenity_ids.pop(index)

    amenity.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['POST'],
                 strict_slashes=False)
def link_amenity_place(place_id, amenity_id):
    """ Links an Amenity and a Place """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)

    place_amenities = place.amenities
    place_amenity = list(filter(lambda a: a.id == amenity_id, place_amenities))
    if place_amenity:  # amenity already exists for this place
        return jsonify(amenity.to_dict())
    if getenv('HBNB_TYPE_STORAGE') == 'db':
        if amenity in place.amenities:
            place.amenities.append(amenity)
    else:
        iplace.amenity_ids.append(amenity_id)
    place.save()
    return make_response(jsonify(amenity.to_dict()), 201)
