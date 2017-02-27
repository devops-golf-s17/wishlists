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


@app.route('/wishlists', methods=['GET'])
def wishlists():
    """
    The route for accessing all wishlist resources or
    creating a new wishlist resource via a POST.
    """
    return db.retrieve_all_wishlists(), HTTP_200_OK


@app.route('/wishlists/<int:wishlist_id>', methods=['GET'])
def read_wishlist(wishlist_id):
    """
    The route for reading wishlists, whether one specifically by id
    or all wishlists when no id is specified.
    """
    try:
        return db.retrieve_wishlist(wishlist_id), HTTP_200_OK
    except WishlistException:
        return jsonify(message='Cannot retrieve wishlist with id %s' % wishlist_id), HTTP_404_NOT_FOUND

@app.route('/wishlists',methods=['POST'])
def add_wishlist():
	# if not request.is_json:
	# 	print "HERE!"
	# 	make_response(CONTENT_ERR_MSG, HTTP_400_BAD_REQUEST)
	name = request.json['name']
	uid = request.json['user_id']
	print name
	print uid
	try:
		# db.create_wishlist(name,user_id)
		return db.create_wishlist(name,uid), HTTP_200_OK
		# return jsonify({'message' :'Wishlist Created successfully'}), 200
	except WishlistException:
		return jsonify(message='Cannot create a new wishlist named %s' % data['name']), HTTP_400_BAD_REQUEST

if __name__ == '__main__':

    # Pull options from environment
    debug = os.getenv('DEBUG', 'False') == 'True'
    port = os.getenv('PORT', '5000')
	
    app.run(host='0.0.0.0', port=int(port), debug=debug)