import os

from flask import Flask, Response, jsonify, request, json, make_response

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

@app.route('/wishlists',methods=['POST'])
def add_wishlist():
	"""
	The route for adding new wishlists, specified by userID and name of the wishlist. You can check 
	the POST requests using CURL.
	Example: curl -i -H 'Content-Type: application/json' -X POST -d '{"name":"Xynazog","user_id":123}' http://127.0.0.1:5000/wishlists
	H is for headers, X is used to specify HTTP Method, d is used to pass a message.
	"""
	name = request.json['name']
	uid = request.json['user_id']
	try:
		return db.create_wishlist(name,uid), HTTP_200_OK
	except WishlistException:
		return jsonify(message='Cannot create a new wishlist named %s' % name), HTTP_400_BAD_REQUEST

@app.route('/wishlists/<int:wishlist_id>/items',methods=['POST'])
def add_item_to_wishlist(wishlist_id):
	"""
	The route for adding new items to the wishlist. This method can also be checked using CURL.
	Pre-requisite: Create a wishlist to add an item.
	Example: curl -i -H 'Content-Type: application/json' -X POST -d '{"id":"i123","description":"Awesome product!"}' http://127.0.0.1:5000/wishlists/1/items
	"""
	tempDic = {}
	tempDic['id'] = request.json['id']
	tempDic['description'] = request.json['description']
	try:
		return db.add_item(wishlist_id,tempDic), HTTP_200_OK
	except WishlistException:
		return jsonify(message='Cannot add a new item %s' % request.json['id']), HTTP_400_BAD_REQUEST


if __name__ == '__main__':

    # Pull options from environment
    debug = os.getenv('DEBUG', 'False') == 'True'
    port = os.getenv('PORT', '5000')
	
    app.run(host='0.0.0.0', port=int(port), debug=debug)