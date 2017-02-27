import os

from flask import Flask, Response, jsonify, request, json

from persistence import db
from persistence.persistence import WishlistNotFoundException, ItemNotFoundException

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
            return 'Could not find a wishlist with id %s' % wishlist_id, HTTP_404_NOT_FOUND


@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['GET'])
def read_wishlist_item(wishlist_id, item_id):
    """
    The route for retrieving a specific item in a wishlist.
    """
    
    try:
        item = db.retrieve_item(wishlist_id, item_id)
        return item, HTTP_200_OK
    except ItemNotFoundException:
        return 'Item with id %s could not be found' % item_id, HTTP_404_NOT_FOUND
    except WishlistNotFoundException:
        return 'Wishlist with id %d could not be found' % wishlist_id, HTTP_404_NOT_FOUND


if __name__ == '__main__':

    # Pull options from environment
    debug = os.getenv('DEBUG', 'False') == 'True'
    port = os.getenv('PORT', '5000')
	
    app.run(host='0.0.0.0', port=int(port), debug=debug)
