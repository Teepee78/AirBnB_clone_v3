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


@app_views.route('states/{state_id}', methods=['GET'])
def states_id(state_id):
	"""Retrieves a State object by its id"""
	states = storage.all(State)
	for state in states.values():
		print(state.id)
		if state.id == state_id:
			return jsonify(state.to_dict())
	return make_response(jsonify({"error": "Not found"}, 404))
