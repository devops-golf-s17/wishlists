# change to test pipeline
# -*- coding: utf-8 -*-

import json
# json.loads() is used to load data from the JSON strings returned by the db

from persistence import db

# NOTE:
# Very basic demo - it's a bit messy but that's why it's in /labs
# a lot of the commands/logic needed for the views in wishlists.py
# can be found here

# Separately - this is not how to do good unit testing :)
# This is more like a template for a README

# create a new wishlist -> POST /wishlists
print '### CREATE WISHLIST TEST ###'
response = json.loads(db.create_wishlist('my_wishlist', 'best_user'))
response = json.loads(db.create_wishlist('my_wishlist', 'new_user'))
wishlist_id = response.get('id')
print 'wishlist_id:{}'.format(wishlist_id)

# add an item -> POST /wishlists/<id>/items
print '### ADD ITEM TEST ###'
ITEM = {
    'id': 'abc123',
    'description': 'cool item'
}
item_create_response = json.loads(db.add_item(wishlist_id, ITEM))
item_id = item_create_response.get('id')

# print specific wishlist and see that items has one element -> GET /wishlists/<id>
print db.retrieve_wishlist(wishlist_id)

# remove an item -> DELETE /wishlists/<id>/items/<id>
print '### REMOVE ITEM TEST ###'
db.remove_item(wishlist_id, item_id)
print 'Success!'

# print all wishlists and verify that items is empty -> GET /wishlists
print '### RETRIEVE ALL WISHLISTS TEST ###'
print db.retrieve_all_wishlists()

# delete wishlist resource and then verify that no more resources are in the db
# -> DELETE /wishlists/<id>
print '### DELETE WISHLIST TEST ###'
db.delete_wishlist(wishlist_id)
print db.retrieve_all_wishlists()

# now add another wishlist, see that the id is 2
print '### ADD SECOND WISHLIST TEST ###'
response_2 = db.create_wishlist('my_new_wishlist', 'jesse')
wishlist_id_2 = json.loads(response_2).get('id')
print 'wishlist id:{}'.format(wishlist_id_2)

# add an item to the wishlist
ITEM_2 = {
    'id': 'def456',
    'description': 'very cool item'
}
item_create_response_2 = json.loads(db.add_item(wishlist_id_2, ITEM_2))
item_id_2 = item_create_response_2.get('id')
print db.retrieve_wishlist(wishlist_id_2)

# let's update the wishlist -> PUT /wishlists/<id>
print '### UPDATE WISHLIST TEST ###'
UPDATE_REQUEST_BODY = {'user_id': 'jessie'}
db.update_wishlist(wishlist_id_2, **UPDATE_REQUEST_BODY)
# we should now see the update
print db.retrieve_wishlist(wishlist_id_2)

# now let's update an item -> PUT /wishlists/<id>/item/<id>
print '### UPDATE ITEM IN WISHLIST ###'
UPDATE_ITEM_REQUEST_BODY = {'description': 'the coolest item ever'}
db.update_wishlist_item(wishlist_id_2, item_id_2, **UPDATE_ITEM_REQUEST_BODY)
# let's verify that the item was updated by returning a list of all items in the db
print db.retrieve_all_items()

# finally, add another wishlist, an item, and then show all wishlists - even the one we deleted
print '### "INTEGRATION" TEST ###'
ITEM_3 = {
    'id': 'ghi789',
    'description': 'somewhat cool item'
}

response_3 = db.create_wishlist('my_best_wishlist', 'mary')
wishlist_3_id = json.loads(response_3).get('id')

db.add_item(wishlist_3_id, ITEM_3)
print db.retrieve_all_wishlists(include_deleted=True)


print "### SEARCH RESULTS ###"
ITEM_4 = {
    'id': 'ada12',
    'description': 'def456 is a cool item indeed!'
}

db.add_item(wishlist_id_2, ITEM_4)
print db.search_all_items("def456","jessie")
