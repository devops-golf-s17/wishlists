# wishlists

[![Build Status](https://travis-ci.org/devops-golf-s17/wishlists.svg?branch=master)](https://travis-ci.org/devops-golf-s17/wishlists)
[![Codecov](https://img.shields.io/codecov/c/github/devops-golf-s17/wishlists.svg)]()

**Wishlists for the e-commerce website.**
Wish lists are collections of desired products saved by customers to their user account, signifying interest without immediate intent to purchase.

## About /labs
Labs is a space where we can put demos and other experimental stuff.
To run .py scripts inside of labs, make sure you are in the root directory and then run
    
    PYTHONPATH=. python labs/<script>.py

## API guide

Below are the supported endpoints:

    GET / 
        -> returns basic API info
    
    POST /wishlists 
        -> create a new wishlist
    
    GET /wishlists 
        -> retrieve all wishlists
        
    GET /wishlists/<int:wishlist_id> 
        -> retrieve a specific wishlist
        
    PUT /wishlists/<int:wishlist_id> 
        -> update a wishlist's data (does not include updates to a wishlist's items)
    
    DELETE /wishlists/<int:wishlist_id>
        -> delete a wishlist by id
    
    POST /wishlists/<int:wishlist_id>/items 
        -> add a new item to a wishlist
        
    GET /wishlist/<int:wishlist_id>/items 
        -> retrieve all items for a wishlist
        
    GET /wishlists/<int:wishlist_id>/items/<string:item_id> 
        -> retrieve an item by id from a wishlist
        
    PUT /wishlists/<int:wishlist_id>/items/<string:item_id>
        -> update a specific item by id from a wishlist
    
    DELETE /wishlists/<int:wishlist_id>/items/<string:item_id>
        -> delete a specific item by id from a wishlist
    
    PUT /wishlists/<int:wishlist_id>/items/clear
        -> clears all items from a wishlist
    
    GET /wishlists/search
        -> Accepts query params <q> and <user_id> in order to search for the value of q
        -> in the items found in a user's wishlists