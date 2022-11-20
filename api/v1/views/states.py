#!/usr/bin/python3
"""This module defines views for state object"""
from flask import jsonify
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

