#!/usr/bin/python3
"""This module is the entry point for flask api"""
from flask import Flask, jsonify
from models import storage
from api.v1.views import app_views
from os import getenv


app = Flask(__name__)
app.register_blueprint(app_views, url_prefix="/api/v1")


@app.teardown_appcontext
def teardown_appcontext(exception):
    """Tear down the app context"""
    storage.close()


@app.errorhandler(404)
def not_found(exception):
	"""404 not found handler"""
	return jsonify({"error": "Not found"})


if __name__ == "__main__":
    host = getenv("HBNB_API_HOST", default="0.0.0.0")
    port = getenv("HBNB_API_PORT", default=5000)
    app.run(host=host, port=int(port), threaded=True)
