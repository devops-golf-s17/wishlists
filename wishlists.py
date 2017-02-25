import os

from flask import Flask, Response, jsonify, request, json

from persistence import db

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409


@app.route('/')
def index():
    wishlist_url = request.base_url + 'wishlists'
    return (jsonify(service='wishlists', version='0.1',
            url=wishlist_url), HTTP_200_OK)

if __name__ == '__main__':

    # Pull options from environment
    debug = os.getenv('DEBUG', 'False') == 'True'
    port = os.getenv('PORT', '5000')
	
    app.run(host='0.0.0.0', port=int(port), debug=debug)