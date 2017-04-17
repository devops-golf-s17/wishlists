import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
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

@app.route('/wishlists', methods=['GET'])
def wishlists():
    """
    The route for accessing all wishlist resources or
    creating a new wishlist resource via a POST.
    """
    wishlistsList = []
    wishlistsList = Wishlist.all()
    print wishlistsList
    for x in wishlistsList:
        print x.serialize_wishlist()
    wishlistsList = [wishlist.serialize_wishlist() for wishlist in wishlistsList]
    return make_response(json.dumps(wishlistsList, indent=4), status.HTTP_200_OK)



@app.route('/wishlists/<int:wishlist_id>', methods=['GET'])
def read_wishlist(wishlist_id):
    """
    The route for reading wishlists, whether one specifically by id
    or all wishlists when no id is specified.
    """
    try:
        wl = Wishlist.find_or_404(wishlist_id)
        return make_response(jsonify(wl.serialize_wishlist()), status.HTTP_200_OK)
    except WishlistException:
        return make_response(jsonify(message='Cannot retrieve wishlist with id %s' % wishlist_id), status.HTTP_404_NOT_FOUND)


@app.route('/wishlists/<int:wishlist_id>/items',methods=['POST'])
def add_item_to_wishlist(wishlist_id):
    """
    The route for adding new items to the wishlist. This method can also be checked using CURL.
    Pre-requisite: Create a wishlist to add an item.
    Example: curl -i -H 'Content-Type: application/json' -X POST -d '{"id":"i123","description":"Awesome product!"}' http://127.0.0.1:5000/wishlists/1/items
    """
    data = request.get_json()
    print data
    if is_valid(data,'item'):
        try:
        	wl = Wishlist.find_or_404(wishlist_id)
        	wl.save_item(data)
        	message = wl.serialize_wishlist()
		return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': wl.self_url()})
        except WishlistException:
            return make_response(jsonify(message='Cannot add a new item %s' % request.json['id']), status.HTTP_400_BAD_REQUEST)
    else:
        message = { 'error' : 'Wishlist %s was not found' % wishlist_id }
        return make_response(jsonify(message), status.HTTP_404_NOT_FOUND)



def is_valid(data, type):
    valid = False
    try:
        if type=='wishlist':
            name=data['name']
            user_id=data['user_id']
            valid=True
        if type=='item':
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
    
