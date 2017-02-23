# -*- coding: utf-8 -*-

from datetime import datetime

from item import Item


class Wishlist(object):
    """
    Simple class for a wishlist that uses a dict as its internal
    store.  Each entry in the dict is another dict that acts as
    an individual "wishlist resource".
    """

    UPDATABLE_FIELDS = ['name']

    def __init__():
        """
        Creates a singleton Wishlist object that manages all
        Wishlist resources.
        """

        # the collection of wishlists that is contained by the class
        self._wishlist_resources = {}
        # the wishlist is a singleton that contains resources in the form of dictionaries;
        # every time a new one is added, the index count goes up like it would in a database
        self._index = 0

    def create_wishlist(name, user_id):
        """
        Make a new wishlist resource with a specified name and user.
        Assuming everything is created OK, return the resource's data
        so that it may be returned to the client who issued the POST.

        :param name: <str> the name to be assigned to the new wishlist
        :param user_id: <str> the id of the user who owns the wishlist
        :return: <dict> the newly created wishlist resource
        """
        new_wishlist = {}
        new_wishlist['name'] = name
        new_wishlist['user_id'] = user_id
        new_wishlist['items'] = {}
        new_wishlist['created'] = datetime.utcnow()
        new_wishlist['deleted'] = False
        self._index += 1
        self._wishlist_resources[self._index] = new_wishlist

        return new_wishlist

    def _verify_wishlist_exists(wishlist_id):
        """
        A quick check that returns True if the wishlist exists and has not
        been deleted.  Otherwise, returns False.

        :param id: <int> the wishlist_id to check
        """

        if wishlist_id in self._wishlist_resources:
            if not wishlist_id['deleted']:
                return True

        return False

    def delete_wishlist(wishlist_id):
        """
        Soft-delete a wishlist resource based on a provided id.
        The soft deletion is implemented as setting the "deleted" field to False.

        :param wishlist_id: <int> the key by which to find a wishlist resource that will be deleted
        """

        try:
            # even if a delete wishlist call was already made, this will just set the value to False again
            self._wishlist_resources[wishlist_id]['deleted'] = False
        except KeyError:
            # cannot delete something that did not exist beforehand
            raise WishlistNotFoundException

    def add_item(wishlist_id, item_data):
        """
        Accepts the id for a wishlist resource, as well
        as data to be used for adding a new item.  It is
        assumed that the caller of this method has *already verified*
        the item_data.

        :param wishlist_id: <int> the id of the wishlist for which to add an item
        :param item_data: <dict> the clean, verified JSON data to be used in making the item

        :return: <dict> the JSON representation of the newly added item resource
        """

        item_id = item_data.get('id')
        item_description = item_data.get('description')

        if self._verify_wishlist_exists(wishlist_id):
            self._wishlist_resources[wishlist_id]['items'][item_id] = {'description': item_description}
            return {'id': item_id, 'description': item_description}
        else:
            raise WishlistNotFoundException

    def remove_item(wishlist_id, item_id):
        """
        Given a wishlist_id and item_id, remove the item in the wishlist
        that matches up with the item_id

        This operation will completely remove the item from the items dictionary.

        :param wishlist_id: <int> the id of the wishlist from which an item will be deleted
        :param item_id: <str> the id of the item to delete
        """

        if self._verify_wishlist_exists(wishlist_id):
            try:
                del self._wishlist_resources[wishlist_id][item_id]
            except KeyError:
                raise WishlistItemNotFoundException
        else:
            # the wishlist does not exist at all
            raise WishlistNotFoundException

    def update_wishlist(wishlist_id, **kwargs):
        """
        Accepts a dictionary of terms and then loops through them to see
        if any match up with the updateable fields specified in the class.
        If there is a match (e.g., kwargs.get('name') has a value), then
        the inputted value overwrites the existing value (and hence 
        performs an update).

        :param wishlist_id: <int> the id of the wishlist to be updated
        :param kwargs: <dict> a variable number of key/value pairs that may contain fields to be updated

        :return: <dict> the modified wishlist resource
        """

        for key in kwargs:
            if key in Wishlist.UPDATABLE_FIELDS:
                # OK to update the field
                self._wishlist_resources[wishlist_id][key] = kwargs.get(key)

        # return the modified resource
        return self._wishlist_resources[wishlist_id]





class WishlistException(Exception):
    """ Generic exception class from which more specific wishlist resource exceptions are derived """


class WishlistNotFoundException(WishlistException):
    """ Raised when a given wishlist resource cannot be found for a specific id """


class WishlistItemNotFoundException(WishlistException):
    """ Raised when a wishlist item is unable to be retrieved """
