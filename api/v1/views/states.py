#!/usr/bin/python3
"""This module defines views for state object"""
from flask import jsonify, make_response

from api.v1.views import app_views
from models import storage
from models.state import State


@app_views.route('/states', methods=['GET'])
def states():
	"""Retrieves the list of all State objects"""
	states = storage.all(State)
	result = []
	
	for state in states.values():
		result.append(state.to_dict())
	return jsonify(result)


@app_views.route('states/<uuid:state_id>', methods=['GET'])
def states_id(state_id):
	"""Retrieves a State object by its id"""
	state = storage.get(State, state_id)
	if state is not None:
		return jsonify(state.to_dict())
	return make_response(jsonify({"error": "Not found"}, 404))
