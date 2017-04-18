import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from custom_exceptions import WishlistException, ItemException
from models import Wishlist
from . import app

import json
from datetime import datetime
# Error handlers require app to be initialized so we must import
# then only after we have initialized the Flask app instance
import error_handlers

redis = None


@app.route('/')
def index():
	#wishlist_url = request.base_url + 'wishlists'
	#return (jsonify(service='wishlists', version='0.1',
	#        url=wishlist_url), HTTP_200_OK)
	return app.send_static_file('index.html')


@app.route('/wishlists',methods=['POST'])
def add_wishlist():
	"""
	The route for adding new wishlists, specified by userID and name of the wishlist. You can check
	the POST requests using CURL.
	Example: curl -i -H 'Content-Type: application/json' -X POST -d '{"name":"Xynazog","user_id":123}' http://127.0.0.1:5000/wishlists
	H is for headers, X is used to specify HTTP Method, d is used to pass a message.
	In location headers, if _external set to True, an absolute URL is generated. 
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
	The route for adding new items to the wishlist. This method can also be checked using CURL.
	Pre-requisite: Create a wishlist to add an item.
	Example: curl -i -H 'Content-Type: application/json' -X POST -d '{"id":"i123","description":"Awesome product!"}' http://127.0.0.1:5000/wishlists/1/items
	curl -i -H 'Content-Type: application/json' -X POST -d '{"id":"i12","description":"Apple product!"}' http://127.0.0.1:5000/wishlists/1/items
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
	The route for accessing all wishlist resources or
	creating a new wishlist resource via a POST.
	"""
	wishlistsList = []
	wishlistsList = Wishlist.all()
	wishlistsList = [wishlist.serialize_wishlist() for wishlist in wishlistsList]
	return make_response(json.dumps(wishlistsList, indent=4), status.HTTP_200_OK)


@app.route('/wishlists/<int:wishlist_id>', methods=['GET'])
def read_wishlist(wishlist_id):
	"""
	The route for reading wishlists, whether one specifically by id
	or all wishlists when no id is specified.
	Example: curl http://127.0.0.1:5000/wishlists/1
	"""
	try:
		wl = Wishlist.find_or_404(wishlist_id)
		return make_response(jsonify(wl.serialize_wishlist()), status.HTTP_200_OK)
	except WishlistException:
		return make_response(jsonify(message='Cannot retrieve wishlist with id %s' % wishlist_id), status.HTTP_404_NOT_FOUND)


@app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
def item(wishlist_id):
	"""
	The route for getting all items associated with a wishlist
	or making a new item for a wishlist via a POST.
	Example: curl http://127.0.0.1:5000/wishlists/1/items
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
	The route for retrieving a specific item in a wishlist.
	Example: curl http://127.0.0.1:5000/wishlists/1/items/i123
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
	The route for modifying a wishlist's user_id or name.
	Example: curl -i -H 'Content-Type: application/json' -X PUT -d '{"name":"new_name","user_id":110}' http://127.0.0.1:5000/wishlists/1
	H is for headers, X is used to specify HTTP Method, d is used to pass a message.
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
	The route for modifying the description of an item in a specific wishlist.
	Example: curl -i -H 'Content-Type: application/json' -X PUT -d '{"description":"update product!"}' http://127.0.0.1:5000/wishlists/1/items/i123
	H is for headers, X is used to specify HTTP Method, d is used to pass a message.
	"""

	data=request.get_json()
	data['id'] = item_id

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
	The route for removing a specific item in a wishlist,
	given a wishlist_id and the item_id
	Example: curl -X DELETE http://127.0.0.1:5000/wishlists/1/items/i123
	"""

	try:
		wl = Wishlist.find_or_404(wishlist_id)
		wl.remove_item(item_id)
		wl.save_wishlist()
		return make_response('', status.HTTP_204_NO_CONTENT)
	except ItemException:
		return make_response(jsonify(message='Item with id %s could not be found' % item_id), status.HTTP_204_NO_CONTENT)
	except WishlistException:
		return make_response(jsonify(message='Wishlist with id %d could not be found' % wishlist_id), status.HTTP_204_NO_CONTENT)



@app.route('/wishlists/<int:wishlist_id>/items/clear', methods=['PUT'])
def clear_wishlist(wishlist_id):
	"""
		The route for clearing a wishlist specified by wishlist_id
		without deleting the wishlist itself.
		Example: curl -X PUT http://127.0.0.1:5000/wishlists/1/items/clear
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
	The route for deleting a specific wishlist when the wishlist_id is specified.
	This only does a soft delete, i.e. update the deleted flag with "true"
	Example: curl -X DELETE http://127.0.0.1:5000/wishlists/1
	"""

	try:
		wl = Wishlist.find_or_404(wishlist_id)
		wl.delete()
		return make_response('', status.HTTP_204_NO_CONTENT)
	except WishlistException:
		return make_response(jsonify(message='Wishlist with id %d could not be found' % wishlist_id), status.HTTP_204_NO_CONTENT)


@app.route('/wishlists/search', methods=['GET'])
def search_wishlists():
	"""
	The route for searching items with specific keyword or ID.
	http://0.0.0.0:5000/wishlists/search?q=Apple&user_id=123
	"""

	data = {}
	data['query'] = request.args.get('q', None)
	data['uid'] = request.args.get('user_id',None)
	wishlists_list = []
	returned_items = []
	wishlists_list = Wishlist.all()
	for wl in wishlists_list:
		item = wl.search_items(data)
		if item:
			returned_items.append(item)
	return make_response(jsonify(returned_items), status.HTTP_200_OK)


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
def inititalize_redis():
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
	
