#!/usr/bin/python3
"""This module defines blueprints"""
from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status')
def status():
    """Returns status information"""
    return jsonify({"status": "OK"})
