# -*- coding: utf-8 -*-

import json
# json.loads() is used to load data from the JSON strings returned
# by the db

from persistence import db

# very basic demo

# create a new wishlist
response = json.loads(db.create_wishlist('my_wishlist', 'best_user'))
wishlist_id = response.get('id')
print 'wishlist_id:{}'.format(wishlist_id)

# add an item
ITEM = {
    'id': 'abc123',
    'description': 'cool item'
}
item_create_response = json.loads(db.add_item(wishlist_id, ITEM))
item_id = item_create_response.get('id')

# print specific wishlist and see that items has one element
print db.retrieve_wishlist_resource(wishlist_id)

# remove an item
db.remove_item(wishlist_id, item_id)

# print all wishlists and verify that items is empty
print db.retrieve_all_wishlist_resources()

# delete wishlist resource and then verify that no more resources are in the db
db.delete_wishlist(wishlist_id)
print db.retrieve_all_wishlist_resources()
