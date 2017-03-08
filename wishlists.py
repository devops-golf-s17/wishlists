import os

from flask import Flask, Response, jsonify, request, json, make_response

from persistence import db

from persistence.persistence import WishlistException, ItemException

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

#db.create_wishlist('jesse','test')

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

@app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
def item(wishlist_id):
    """
    The route for getting all items associated with a wishlist
    or making a new item for a wishlist via a POST.
    """

    if request.method == 'GET':
        try:
            items = db.retrieve_all_items(wishlist_id)
            return items, HTTP_200_OK
        except WishlistException:
            return jsonify(message='Could not find a wishlist with id %s' % wishlist_id), HTTP_404_NOT_FOUND

@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['GET'])
def read_wishlist_item(wishlist_id, item_id):
    """
    The route for retrieving a specific item in a wishlist.
    """

    try:
        item = db.retrieve_item(wishlist_id, item_id)
        return item, HTTP_200_OK
    except ItemException:
        return jsonify(message='Item with id %s could not be found' % item_id), HTTP_404_NOT_FOUND
    except WishlistException:
        return jsonify(message='Wishlist with id %d could not be found' % wishlist_id), HTTP_404_NOT_FOUND

@app.route('/wishlists/<int:id>', methods=['PUT'])
def update_wishlist(id):
    """
    The route for modifying a wishlist's user_id or name.
    """

    try:
        data = request.get_json()
        return db.update_wishlist(id, **data), HTTP_200_OK
    except WishlistException:
        message = { 'error' : 'Wishlist %s was not found' % id }
        return jsonify(message), HTTP_404_NOT_FOUND

@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['PUT'])
def update_wishlist_item(wishlist_id, item_id):
    """
    The route for modifying the description of an item in a specific wishlist.
    """

    try:
        data = request.get_json()
        return db.update_wishlist_item(wishlist_id, item_id, **data ), HTTP_200_OK
    except WishlistException:
        message = { 'error' : 'Wishlist %s was not found' % wishlist_id }
        return jsonify(message), HTTP_404_NOT_FOUND
    except ItemException:
        message = { 'error' : 'Item %s was not found' % item_id }
        return jsonify(message), HTTP_404_NOT_FOUND

@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['DELETE'])
def remove_wishlist_item(wishlist_id, item_id):
    """
    The route for removing a specific item in a wishlist,
    given a wishlist_id and the item_id
    """

    try:
        db.remove_item(wishlist_id, item_id)
        return '', HTTP_204_NO_CONTENT
    except ItemException:
        return jsonify(message='Item with id %s could not be found' % item_id), HTTP_404_NOT_FOUND
    except WishlistException:
        return jsonify(message='Wishlist with id %d could not be found' % wishlist_id), HTTP_404_NOT_FOUND

@app.route('/wishlists/<int:wishlist_id>/items/clear', methods=['PUT'])
def clear_wishlist(wishlist_id):
    """
        The route for clearing a wishlist specified by wishlist_id
	without deleting the wishlist itself.
    """

    try:
        wl_info = db.retrieve_wishlist(wishlist_id)
        wl = json.loads(wl_info)
        items_dict = wl["items"]

        for key,value in items_dict.iteritems():
            try:
                db.remove_item(wishlist_id, key)
            except ItemException:
                message = { 'error' : 'Item %d was not found' % value}
                return jsonify(message), HTTP_404_NOT_FOUND
        return db.retrieve_wishlist(wishlist_id), HTTP_200_OK
    except WishlistException:
        message = { 'error' : 'Wishlist %s was not found' % wishlist_id }
        return jsonify(message), HTTP_404_NOT_FOUND

@app.route('/wishlists/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(wishlist_id):
    """
    The route for deleting a specific wishlist when the wishlist_id is specified.
    This only does a soft delete, i.e. update the deleted flag with "true"
    """

    try:
        db.delete_wishlist(wishlist_id)
        return '', HTTP_204_NO_CONTENT
    except WishlistException:
        return jsonify(message='Wishlist with id %d could not be found' % wishlist_id), HTTP_404_NOT_FOUND


if __name__ == '__main__':

    # Pull options from environment
    debug = os.getenv('DEBUG', 'False') == 'True'
    port = os.getenv('PORT', '5000')

    app.run(host='0.0.0.0', port=int(port), debug=debug)
