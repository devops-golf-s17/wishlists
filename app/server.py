import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from flasgger import Swagger
from custom_exceptions import WishlistException, ItemException
from models import Wishlist
from . import app

import json
from datetime import datetime
# Error handlers require app to be initialized so we must import
# then only after we have initialized the Flask app instance
import error_handlers

redis = None



# Initialize Swagger after configuring it
Swagger(app)

@app.route('/')
def index():
	#wishlist_url = request.base_url + 'wishlists'
	#return (jsonify(service='wishlists', version='0.1',
	#        url=wishlist_url), HTTP_200_OK)
	return app.send_static_file('index.html')


@app.route('/wishlists',methods=['POST'])
def add_wishlist():
	"""
    Creates a Wishlist
    This endpoint will create a Wishlist based on the data in the body that is posted
    ---
    tags:
      - Wishlists
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - name
            - category
          properties:
            name:
              type: string
              description: name for the Wishlist
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
    responses:
      201:
        description: Wishlist created
        schema:
          id: Wishlist
          properties:
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
            name:
              type: string
              description: Wishlist Name(created by the user)
            created:
              type: string
              format: date-time
              description: The time at which the wishlist was created
            deleted:
              type: boolean
              description: Flag to be set when a wishlist is deleted
            items:
              type: object
              properties:
                wishlist_item_id:
                  type: object
                  properties:
                    item_id:
                      type: string
                      description: Original ID of the item
                    item_description:
                      type: string
                      description: Description of the item
              description: Dictionary to store objects in a wishlist
            id:
              type: integer
              description: Unique ID of the wishlist assigned internally by the server
      400:
        description: Bad Request (the posted data was not valid)
    """

	data = request.get_json()
	if is_valid(data,'wishlist'):
		wishl = Wishlist()
		wishl.deserialize_wishlist(data)
		wishl.save_wishlist()
		message = wishl.serialize_wishlist()
		return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': wishl.self_url()})
	else:
		message = {'error' : 'Wishlist data was not valid'}
		return make_response(jsonify(message), status.HTTP_400_BAD_REQUEST)


@app.route('/wishlists/<int:wishlist_id>/items',methods=['POST'])
def add_item_to_wishlist(wishlist_id):
	"""
    Add a Wishlist Item to an existing wishlist
    This endpoint will add a wishlist item based on the data in the body that is posted
    ---
    tags:
      - Wishlist Items
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: wishlist_id
        in: path
        description: ID of wishlist to which the item has to be added to
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - id
            - description
          properties:
            id:
              type: string
              description: ID of the wishlist item
            description:
              type: string
              description: Description of the item to be added to the wishlist
    responses:
      201:
        description: Wishlist item created
        schema:
          id: Wishlist
          properties:
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
            name:
              type: string
              description: Wishlist Name(created by the user)
            created:
              type: string
              format: date-time
              description: The time at which the wishlist was created
            deleted:
              type: boolean
              description: Flag to be set when a wishlist is deleted
            items:
              type: object
              properties:
                wishlist_item_id:
                  type: object
                  properties:
                    item_id:
                      type: string
                      description: Original ID of the item
                    item_description:
                      type: string
                      description: Description of the item
              description: Dictionary to store objects in a wishlist
            id:
              type: integer
              description: Unique ID of the wishlist assigned internally by the server
      400:
        description: Bad Request (the posted data was not valid)
    """
	data = request.get_json()
	if is_valid(data,'item'):
		try:
			wl = Wishlist.find_or_404(wishlist_id)
			wl.deserialize_wishlist_items(data)
			wl.save_item()
			message = wl.serialize_wishlist()
			return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': wl.self_url()})
		except WishlistException:
			message = { 'error' : 'Wishlist %s was not found' % wishlist_id }
			return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
	else:
		message = {'error' : 'Item data was not valid'}
		return make_response(jsonify(message), status.HTTP_400_BAD_REQUEST)



@app.route('/wishlists', methods=['GET'])
def wishlists():
	"""
    Retrieve a list of Wishlists
    This endpoint will return all wishlists
    ---
    tags:
      - Wishlists
    responses:
      200:
        description: An array of Wishlists
        schema:
          type: array
          items:
            schema:
              id: Wishlist
              properties:
                user_id:
                  type: string
                  description: Unique ID of the user(created by the user)
                name:
                  type: string
                  description: Wishlist Name(created by the user)
                created:
                  type: string
              	  format: date-time
                  description: The time at which the wishlist was created
                deleted:
                  type: boolean
                  description: Flag to be set when a wishlist is deleted
                items:
              	  type: object
              	  properties:
              	  	wishlist_item_id:
              	  	  type: object
              	  	  properties:
              	  	  	item_id:
              	  	  	  type: string
              	  	  	item_description:
              	  	  	  type: string
                  description: Dictionary to store objects in a wishlist
                id:
                  type: integer
                  description: Unique ID of the wishlist assigned internally by the server
    """
	wishlistsList = []
	wishlistsList = Wishlist.all()
	wishlistsList = [wishlist.serialize_wishlist() for wishlist in wishlistsList]
	return make_response(json.dumps(wishlistsList, indent=4), status.HTTP_200_OK)


@app.route('/wishlists/<int:wishlist_id>', methods=['GET'])
def read_wishlist(wishlist_id):
	"""
    Retrieve a single Wishlist
    This endpoint will return a Wishlist based on it's ID
    ---
    tags:
      - Wishlists
    produces:
      - application/json
    parameters:
      - name: wishlist_id
        in: path
        description: ID of wishlist to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Wishlist retrieved
        schema:
          id: Wishlist
          properties:
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
            name:
              type: string
              description: Wishlist Name(created by the user)
            created:
              type: string
              format: date-time
              description: The time at which the wishlist was created
            deleted:
              type: boolean
              description: Flag to be set when a wishlist is deleted
            items:
              type: object
              properties:
                wishlist_item_id:
                  type: object
                  properties:
                    item_id:
                      type: string
                      description: Original ID of the item
                    item_description:
                      type: string
                      description: Description of the item
              description: Dictionary to store objects in a wishlist
            id:
              type: integer
              description: Unique ID of the wishlist assigned internally by the server
      404:
        description: Wishlist not found
    """
	try:
		wl = Wishlist.find_or_404(wishlist_id)
		return make_response(jsonify(wl.serialize_wishlist()), status.HTTP_200_OK)
	except WishlistException:
		return make_response(jsonify(message='Cannot retrieve wishlist with id %s' % wishlist_id), status.HTTP_404_NOT_FOUND)


@app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
def item(wishlist_id):
	"""
    Retrieve a list of items in the wishlist
    This endpoint will return all items
    ---
    tags:
      - Wishlist Items
    parameters:
      - name: wishlist_id
        in: path
        description: ID of the wishlist from which items have to be retrieved
        required: true
        type: integer
    responses:
      200:
        description: Wishlist items belonging to the wishlist ID
        schema:
        	id: Wishlist
        	properties:
			  	wishlist_item_id:
			  		type: object
			  		properties:
			  			item_id:
			  				type: string
			  				description: ID of the item
			  			item_description:
			  				type: string
			  				description: Description of the item


      404:
        description: Wishlist not found
    """
	try:
		wl = Wishlist.find_or_404(wishlist_id)
		items = wl.all_items()
		return make_response(jsonify(items), status.HTTP_200_OK)
	except WishlistException:
		return make_response(jsonify(message='Cannot retrieve wishlist with id %s' % wishlist_id), status.HTTP_404_NOT_FOUND)


@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['GET'])
def read_wishlist_item(wishlist_id, item_id):
	"""
    Retrieve a single Wishlist item
    This endpoint will return a Wishlist item based on it's ID
    ---
    tags:
      - Wishlist Items
    produces:
      - application/json
    parameters:
      - name: wishlist_id
        in: path
        description: ID of wishlist to retrieve from
        type: integer
        required: true
      - name: item_id
      	in: path
      	description: ID of item to be retrieved
      	type: string
      	required: true
    responses:
      200:
        description: Wishlist items matching with the query
        schema:
          id: Wishlist
          properties:
            id:
              type: string
              description: ID of the item matching
            description:
              type: string
              description: Description of the item
      404:
        description: Wishlist not found
    """
	try:
		wl = Wishlist.find_or_404(wishlist_id)
		item = wl.find_item(item_id)
		return make_response(jsonify(item), status.HTTP_200_OK)
	except ItemException:
		return make_response(jsonify(message='Item with id %s could not be found' % item_id), status.HTTP_404_NOT_FOUND)
	except WishlistException:
		return make_response(jsonify(message='Wishlist with id %d could not be found' % wishlist_id), status.HTTP_404_NOT_FOUND)


@app.route('/wishlists/<int:id>', methods=['PUT'])
def update_wishlist(id):
	"""
    Update a Wishlist
    This endpoint will update a Wishlist based on the body that is put
    ---
    tags:
      - Wishlists
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of wishlist to update
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - user_id
          properties:
            name:
              type: string
              description: New name for the Wishlist
            user_id:
              type: string
              description: User ID of the user owning the wishlist
    responses:
      200:
        description: Wishlist updated
        schema:
          id: Wishlist
          properties:
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
            name:
              type: string
              description: Wishlist Name(created by the user)
            created:
              type: string
              format: date-time
              description: The time at which the wishlist was created
            deleted:
              type: boolean
              description: Flag to be set when a wishlist is deleted
            items:
              type: object
              properties:
                wishlist_item_id:
                  type: object
                  properties:
                    item_id:
                      type: string
                      description: Original ID of the item
                    item_description:
                      type: string
                      description: Description of the item
              description: Dictionary to store objects in a wishlist
            id:
              type: integer
              description: Unique ID of the wishlist assigned internally by the server
      404:
      	description: Wishlist not found
      400:
        description: Bad Request (the posted data was not valid)
    """
	data = request.get_json()
	if is_valid(data, 'wishlist'):
		try:
			wl = Wishlist.find_or_404(id)
			wl.deserialize_wishlist(data)
			wl.save_wishlist()
			return make_response(jsonify(wl.serialize_wishlist()), status.HTTP_200_OK)
		except WishlistException:
			message = { 'error' : 'Wishlist %s was not found' % id }
			return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
	else:
		message = {'error' : 'Wishlist data was not valid'}
		return make_response(jsonify(message), status.HTTP_400_BAD_REQUEST)


@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['PUT'])
def update_wishlist_item(wishlist_id, item_id):
	"""

    Update a Wishlist Item
    This endpoint will update a Wishlist Item based the body that is posted
    ---
    tags:
      - Wishlist Items
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: wishlist_id
        in: path
        description: ID of wishlist to which the item belongs
        type: integer
        required: true
      - name: item_id
      	in: path
      	description: ID of Item to be updated
      	type: String
      	required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - description
          properties:
            description:
              type: string
              description: Updated description of the item
    responses:
      200:
        description: Wishlist item updated
        schema:
          id: Wishlist
          properties:
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
            name:
              type: string
              description: Wishlist Name(created by the user)
            created:
              type: string
              format: date-time
              description: The time at which the wishlist was created
            deleted:
              type: boolean
              description: Flag to be set when a wishlist is deleted
            items:
              type: object
              properties:
                wishlist_item_id:
                  type: object
                  properties:
                    item_id:
                      type: string
                      description: Original ID of the item
                    item_description:
                      type: string
                      description: Description of the item
              description: Dictionary to store objects in a wishlist
            id:
              type: integer
              description: Unique ID of the wishlist assigned internally by the server
      404:
      	description: Wishlist/Item not found.
      400:
        description: Bad Request (the posted data was not valid)
    """
	try:
		data=request.get_json()
		data['id'] = item_id
	except TypeError:
		( jsonify("Invalid input data type"), status.HTTP_400_BAD_REQUEST )

	if is_valid(data, 'item'):
		try:
			wl = Wishlist.find_or_404(wishlist_id)
			wl.update_item(data)
			wl.save_wishlist()
			new_wl = wl.find(wishlist_id)
			return make_response(jsonify(new_wl.serialize_wishlist()), status.HTTP_200_OK)
		except WishlistException:
			message = { 'error' : 'Wishlist %s was not found' % wishlist_id }
			return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
		except ItemException:
			message = { 'error' : 'Item %s was not found' % item_id }
			return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)
	else:
		message = {'error' : 'Item data was not valid'}
		return make_response(jsonify(message), status.HTTP_400_BAD_REQUEST)


@app.route('/wishlists/<int:wishlist_id>/items/<string:item_id>', methods=['DELETE'])
def remove_wishlist_item(wishlist_id, item_id):
	"""
	Delete a Wishlist item
    This endpoint will delete an item based on the id specified in the path
    ---
    tags:
      - Wishlist Items
    description: Deletes a Wishlist Item from the database
    parameters:
      - name: wishlist_id
        in: path
        description: ID of the wishlist
        type: string
        required: true
      - name: item_id
      	in: path
      	description: ID of the item to be deleted
      	type: string
      	required: true
    responses:
      204:
        description: Item deleted
	"""
	wl = Wishlist.find(wishlist_id)
	if not wl:
		return make_response(jsonify(message='Wishlist with id %d could not be found' % wishlist_id), status.HTTP_204_NO_CONTENT)
	try:
		wl.remove_item(item_id)
		wl.save_wishlist()
		return make_response('', status.HTTP_204_NO_CONTENT)
	except ItemException:
		message = { 'error' : 'Item %s was not found' % item_id }
		return make_response(jsonify(message), status.HTTP_204_NO_CONTENT)


@app.route('/wishlists/<int:wishlist_id>/items/clear', methods=['PUT'])
def clear_wishlist(wishlist_id):
	"""
    Clears a Wishlist
    This endpoint will clear a Wishlist based on the wishlist_id
    ---
    tags:
      - Wishlists
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: wishlist_id
      	in: path
      	description: ID of the wishlist to be cleared
      	type: integer
      	required: true
    responses:
      200:
        description: Wishlist cleared
        schema:
          id: Wishlist
          properties:
            user_id:
              type: string
              description: Unique ID of the user(created by the user)
            name:
              type: string
              description: Wishlist Name(created by the user)
            created:
              type: string
              format: date-time
              description: The time at which the wishlist was created
            deleted:
              type: boolean
              description: Flag to be set when a wishlist is deleted
            items:
              type: object
              properties:
                wishlist_item_id:
                  type: object
                  properties:
                    item_id:
                      type: string
                      description: Original ID of the item
                    item_description:
                      type: string
                      description: Description of the item
              description: Dictionary to store objects in a wishlist
            id:
              type: integer
              description: Unique ID of the wishlist assigned internally by the server
      404:
        description: Wishlist not found
    """
	try:
		wl = Wishlist.find_or_404(wishlist_id)
		wl.remove_item(None)
		wl.save_wishlist()
		new_wl = wl.find(wishlist_id)
		return make_response(jsonify(new_wl.serialize_wishlist()), status.HTTP_200_OK)
	except WishlistException:
		message = { 'error' : 'Wishlist %s was not found' % wishlist_id }
		return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)


@app.route('/wishlists/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(wishlist_id):
	"""
	Delete a Wishlist
    This endpoint will delete a Wishlist based on the id specified in the path
    ---
    tags:
      - Wishlists
    description: Deletes a Wishlist from the database
    parameters:
      - name: wishlist_id
        in: path
        description: ID of the wishlist to delete
        type: integer
        required: true
    responses:
      204:
        description: Wishlist deleted
	"""


	wl = Wishlist.find(wishlist_id)
	if wl:
		wl.delete()
		return make_response('', status.HTTP_204_NO_CONTENT)
	else:
		return make_response(jsonify(message='Wishlist with id %d could not be found' % wishlist_id), status.HTTP_204_NO_CONTENT)


@app.route('/wishlists/search', methods=['GET'])
def search_wishlists():
	"""
	Search a Wishlist Item
    This endpoint will return a Wishlist Item based on the query parameters
    ---
    tags:
      - Wishlist Items
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: q
        in: query
        description: Query to be searched
        type: string
        required: true
      - name: user_id
      	in: query
      	description: User ID whose wishlists would be searched
      	type: String
    responses:
      200:
        description: Wishlist items matching with the query
        schema:
          type: object
          properties:
            Search results for keyword \"IPhone\" in wishlists user ID \"user3\":
              type: array
              items:
                schema:
                  id: Wishlist
                  properties:
                    Results from wishlist with ID 3:
                      type: object
                      properties:
                        item_id:
                          type: string
                          example: a12
                          description: ID of the item matching
                        item_description:
                          type: string
                          example: Product (Red) iPhone 7 Plus 256 GB
                          description: Description of the item
      400:
        description: userid is missing
	"""

	data = {}
	data['query'] = request.args.get('q', None)
	data['uid'] = request.args.get('user_id',None)
	if data['uid'] is None:
		return make_response(jsonify("Error: userid is missing"), status.HTTP_400_BAD_REQUEST)
	wishlists_list = []
	returned_items = []
	wishlists_list = Wishlist.all()
	for wl in wishlists_list:
		item = wl.search_items(data)
		if item:
			returned_items.append(item)
	message = 'Search results for keyword \"%s\" in wishlists with user ID \"%s\"' % (data['query'], data['uid'])
	ret = {message : returned_items}
	return make_response(jsonify(ret), status.HTTP_200_OK)


def is_valid(data, type):
	valid = False
	try:
		if type=='wishlist':
			name=data['name']
			user_id=data['user_id']
			valid=True
		if type=='item':
			id = data['id']
			description=data['description']
			valid=True
	except KeyError as e:
		app.logger.warn('Missing parameter: %p', e)
	except TypeError as e:
		app.logger.warn('Invalid Content Type: %c', e)
	return valid


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
# load sample data
def data_load_wishlist(data):
	Wishlist().deserialize_wishlist(data).save_wishlist()

# empty the database
def data_reset():
	redis.flushall()

def data_load_wishlist_items(data):
	#data_to_be_sent = {"id":data['id'], "description":data['description']}
	wl = Wishlist.find_or_404(data['wishlist_id'])
	wl.deserialize_wishlist_items(data).save_item()


######################################################################
# Connect to Redis and catch connection exceptions
######################################################################
def connect_to_redis(hostname, port, password):
	redis = Redis(host=hostname, port=port, password=password)
	try:
		redis.ping()
	except ConnectionError:
		redis = None
	return redis


######################################################################
# INITIALIZE Redis
# This method will work in the following conditions:
#   1) In Bluemix with Redis bound through VCAP_SERVICES
#   2) With Redis running on the local server as with Travis CI
#   3) With Redis --link ed in a Docker container called 'redis'
######################################################################

def initialize_redis():

	global redis
	redis = None
	# Get the credentials from the Bluemix environment
	if 'VCAP_SERVICES' in os.environ:
		app.logger.info("Using VCAP_SERVICES...")
		VCAP_SERVICES = os.environ['VCAP_SERVICES']
		services = json.loads(VCAP_SERVICES)
		creds = services['rediscloud'][0]['credentials']
		app.logger.info("Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port']))
		redis = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
	else:
		app.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
		redis = connect_to_redis('127.0.0.1', 6379, None)
		if not redis:
			app.logger.info("No Redis on localhost, using: redis")
			redis = connect_to_redis('redis', 6379, None)
	if not redis:
		# if you end up here, redis instance is down.
		app.logger.error('*** FATAL ERROR: Could not connect to the Redis Service')
	# Have the Wishlist model use Redis
	Wishlist.use_db(redis)
