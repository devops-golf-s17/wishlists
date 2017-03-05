# -*- coding: utf-8 -*-

import json
from datetime import datetime


class DatabaseEngine(object):
    """
    Simple class for a persistence layer interface that uses a dict as 
    its internal store.  Each entry in the dict is another dict that
    acts as an individual "wishlist resource".
    """

    UPDATABLE_WISHLIST_FIELDS = ['user_id', 'name']
    UPDATABLE_ITEM_FIELDS = ['description']

    def __init__(self):
        """
        Initializes the internal store of wishlist resources.
        """

        # the collection of wishlists that is contained by the class
        self._wishlist_resources = {}
        # the wishlist is a singleton that contains resources in the form of dictionaries;
        # every time a new one is added, the index count goes up like it would in a database
        self._index = 0

    def create_wishlist(self, name, user_id):
        """
        Make a new wishlist resource with a specified name and user.
        Assuming everything is created OK, return the resource's data
        so that it may be returned to the client who issued the POST.

        :param name: <str> the name to be assigned to the new wishlist
        :param user_id: <str> the id of the user who owns the wishlist

        :return: <str> the newly created wishlist resource in JSON string form
        """
        new_wishlist = {}
        new_wishlist['name'] = name
        new_wishlist['user_id'] = user_id
        new_wishlist['items'] = []
        # get a nicely formatted, human-readable datetime
        new_wishlist['created'] = str(datetime.utcnow())
        new_wishlist['deleted'] = False
        self._index += 1
        new_wishlist['id'] = self._index
        self._wishlist_resources[self._index] = new_wishlist

        return json.dumps(new_wishlist, indent=4)

    def _verify_wishlist_exists(self, wishlist_id):
        """
        A quick check that returns True if the wishlist exists and has not
        been deleted.  Otherwise, returns False.

        :param id: <int> the wishlist_id to check

        :return: <bool> whether or not the wishlist exists
        """

        if wishlist_id in self._wishlist_resources:
            if not self._wishlist_resources[wishlist_id]['deleted']:
                return True

        return False

    def _collect_items(self, wishlist_id):
        """
        Private method for neatly collecting all items in a wishlist and returning
        them for use elsewhere.  It is assumed that the wishlist has already been confirmed to
        exist prior to passing in the id.

        :param wishlist_id: <int> the id of the wishlist whose items should be collected

        :return: <list> a list of dict objects
        """

        items = self._wishlist_resources[wishlist_id]['items']
        return items
    
    def _retrieve_item(self, wishlist_id, item_id=None, item_index=None):
        """
        Private method that does the work for the public retrieve_item; namely,
        performs a "smart" search for an item based on the parameters that exist.
        If item_id exists, then a search is performed to find an item with a matching
        id.  Otherwise, if item_index is passed in then a search is performed based on
        index.  Either way, the result of the search is passed back for retrieve_item to process.

        :param item_id: <str> the unique id of the item
        :param item_index: <int> the index id of the item in the item collection

        :return: <Item|None> the item object if it was found, or None if it was not
        """
        desired_item = None

        if item_id:
            # we have already verified that the wishlist exists in retrieve_item
            all_items = self._collect_items(wishlist_id)
            for item in all_items:
                if item.get('item_id') == item_id:
                    desired_item = item
            
            if desired_item:
                return json.dumps(desired_item, indent=4)
            else:
                return desired_item

        elif item_index:
            # query by the index of the item list
            try:
                desired_item = self._collect_items(wishlist_id)[item_index]
                return desired_item
            except IndexError:
                return None

    def delete_wishlist(self, wishlist_id):
        """
        Soft-delete a wishlist resource based on a provided id.
        The soft deletion is implemented as setting the "deleted" field to False.

        :param wishlist_id: <int> the key by which to find a wishlist resource that will be deleted
        """

        try:
            # even if a delete wishlist call was already made, this will just set the value to True again
            self._wishlist_resources[wishlist_id]['deleted'] = True
        except KeyError:
            # cannot delete something that did not exist beforehand
            raise WishlistNotFoundException

    def add_item(self, wishlist_id, new_item_data):
        """
        Accepts the id for a wishlist resource, as well
        as data to be used for adding a new item.  It is
        assumed that the caller of this method has *already verified*
        the item_data.

        :param wishlist_id: <int> the id of the wishlist for which to add an item
        :param item_data: <dict> the clean, verified JSON data to be used in making the item

        :return: <str> the JSON string representation of the newly added item resource
        """

        new_item_id = new_item_data.get('item_id')
        new_item_description = new_item_data.get('description')

        if self._verify_wishlist_exists(wishlist_id):
            wishlist_items = self._collect_items(wishlist_id)
            number_of_items = len(wishlist_items)
            for item in wishlist_items:
                if new_item_id == item.get('item_id'):
                    # one cannot add an item that already exists
                    # note: although it would not be an issue to merely overwrite the data,
                    # that would not be a proper result of a POST request to add an item
                    raise WishlistOperationNotPermittedException
                else:
                    # add a new item
                    self._wishlist_resources[wishlist_id]['items'].append(
                        {
                            'item_id': new_item_id,
                            'description': new_item_description
                        }
                    )
                    # we may decide to make the index more "user-friendly" in the future (i.e., all indices > 1)
                    # note that the length of the list prior to adding the item is actually the index of the new item
                    return json.dumps(
                        {
                            'item_index': number_of_items,
                            'item_id': new_item_id,
                            'description': new_item_description
                        },
                        indent=4
                    )
        else:
            raise WishlistNotFoundException

    def remove_item(self, wishlist_id, item_id=None, item_index=None):
        """
        Given a wishlist_id and item_id, remove the item in the wishlist
        that matches up with the item_id

        This operation will completely remove the item from the items dictionary.

        :param wishlist_id: <int> the id of the wishlist from which an item will be deleted
        :param item_id: <str|None> the id of the item to delete
        :param item_index: <int|None> the index of the item in the wishlist's items collection
        """

        if self._verify_wishlist_exists(wishlist_id):

            if item_id:
                # get item via its unique id
                item_to_remove = self._retrieve_item(wishlist_id, item_id=item_id)

            elif item_index:
                # get item via its index
                item_to_remove = self._retrieve_item(wishlist_id, item_index=item_index)

            if item_to_remove:
                item_to_remove_index = self._wishlist_resources[wishlist_id]['items'].index(item_to_remove)
                del self._wishlist_resources[wishlist_id]['items'][item_to_remove_index]
            else:
                raise ItemNotFoundException

        else:
            # the wishlist does not exist or has been deleted
            raise WishlistNotFoundException

    def update_wishlist(self, wishlist_id, **kwargs):
        """
        NOTE: You must pass in a dictionary with "**" in front of it for the kwargs argument.
        As of right now this is probably excessive since we only have one field that can be
        updated, but it will be useful later on.

        Accepts a wishlist_id and a dictionary of terms and then loops through them to see
        if any match up with the updateable fields specified in the class.
        If there is a match (e.g., kwargs.get('name') has a value), then
        the inputted value overwrites the existing value (and hence 
        performs an update).

        :param wishlist_id: <int> the id of the wishlist to be updated
        :param kwargs: <dict> a variable number of key/value pairs that may contain fields to be updated

        :return: <str> the modified wishlist resource as a JSON string
        """
        if self._verify_wishlist_exists(wishlist_id):
            for key in kwargs:
                if key in DatabaseEngine.UPDATABLE_WISHLIST_FIELDS:
                    # OK to update the field
                    self._wishlist_resources[wishlist_id][key] = kwargs.get(key)

            # return the modified resource
            return json.dumps(self._wishlist_resources[wishlist_id], indent=4)
        else:
            raise WishlistNotFoundException

    def update_wishlist_item(self, wishlist_id, item_id=None, item_index=None, **kwargs):
        """
        NOTE: You must pass in a dictionary with "**" in front of it for the kwargs argument.
        As of right now this is probably excessive since we only have one field that can be
        updated, but it will be useful later on.

        Accepts a wishlist_id, item_id, and a dictioanry of terms before
        looping through them to see if any match up with the updateable fields
        specified in the class. If there is a match (e.g., kwargs.get('name') has a value),
        then the inputted value overwrites the existing value
        (and hence performs an update).

        :param wishlist_id: <int> the id of the wishlist to which the item to be modified belongs
        :param item_id: <str|None> the id of the item to be modified
        :param item_index: <int|None> the index of the item in the wishlist's items collection

        :param kwargs: <dict> a variable number of key/value pairs that may contain fields to be updated

        :return: <str> the modified wishlist resource as a JSON string
        """

        if self._verify_wishlist_exists(wishlist_id):

            if item_id:
                items = self._collect_items(wishlist_id)
                item_found = False
                # not efficient or elegant, but this will be deprecated once we have proper db support
                for item in items:
                    if item.get('item_id') == item_id:
                        item_found = True
                        matching_item_index = items.index(item)
                        for key in kwargs:
                            if key in DatabaseEngine.UPDATABLE_ITEM_FIELDS:
                                self._wishlist_resources[wishlist_id]['items'][matching_item_index][key] = kwargs.get(key)
                if not item_found:
                    # if we didn't find a matching item after iterating through all items
                    raise ItemNotFoundException

            elif item_index:
                # much easier this way
                try:
                    for key in kwargs:
                        if key in DatabaseEngine.UPDATABLE_ITEM_FIELDS:
                            self._wishlist_resources[wishlist_id]['items'][item_index][key] = kwargs.get(key)
                except IndexError:
                    raise ItemNotFoundException

        else:
            raise WishlistNotFoundException

    def retrieve_wishlist(self, wishlist_id):
        """
        Given a specific wishlist_id, return the corresponding resource or raise
        an exception if it cannot be found.

        :param wishlist_id: <str> the id for the wishlist to be returned

        :return: <str> the JSON string representation of the desired wishlist resource
        """

        if self._verify_wishlist_exists(wishlist_id):
            return json.dumps(self._wishlist_resources[wishlist_id], indent=4)
        else:
            raise WishlistNotFoundException

    def retrieve_all_wishlists(self, include_deleted=False):
        """
        Returns a list of all existing wishlist resources.  Note that
        deleted resources are *not* included by default; this flag must
        be explicitly set by passing in include_deleted=True.

        :param include_deleted: <bool> whether or not to include soft-deleted wishlists in the returned list

        :return: <str> the JSON string representation of all wishlists
        """

        all_wishlists = []

        if include_deleted:
            # use a list comprehension to easily retrieve the dictionaries and merge them together into a JSON string
            all_wishlists = [{key: contents} for key, contents in self._wishlist_resources.iteritems()]
        else:
            # filter out those key, contents pairs where contents['deleted'] == True 
            all_wishlists = [{key: contents} for key, contents in self._wishlist_resources.iteritems() if contents['deleted'] == False]

        return json.dumps(all_wishlists, indent=4)
    
    def retrieve_item(self, wishlist_id, item_id=None, item_index=None):
        """
        Collect a specific item associated with a wishlist.

        :param wishlist_id: <int> the wishlist from which an item will be retrieved
        :param item_id: <str|None> the id of the item to be retrieved
        :param item_index: <int|None> the index of the item in the wishlist's items collection

        :return: <str> a JSON string representation of the desired item resource
        """
        
        if self._verify_wishlist_exists(wishlist_id):
            item = None

            if item_id:
                # retrieve item based on its unique id
                item = self._retrieve_item(wishlist_id, item_id=item_id)
            
            elif item_index:
                # retrieve item based on its index in the item collection
                item = self._retrieve_item(wishlist_id, item_index=item_index)

            if item:
                return json.dumps(item, indent=4)
            else:
                raise ItemNotFoundException
        else:
            raise WishlistNotFoundException

    def retrieve_all_items(self, wishlist_id=None):
        """
        Collect all items in a given wishlist if an id is provided, else collect all
        items across all wishlists.  Returns a JSON string containing serializations
        of all items.

        :param wishlist_id: <int|None> an id for a specific wishlist from which to return the list of items

        :return: <list> a JSON string representation of all items in one wishlist or all wishlists
        """
        items_to_retrieve = {}

        if wishlist_id:
            if self._verify_wishlist_exists(wishlist_id):
                # collect all items from single wishlist
                items_to_retrieve[wishlist_id] = self._collect_items(wishlist_id)
            else:
                raise WishlistNotFoundException
        else:
            # collect all items from all wishlists
            for wishlist_key in self._wishlist_resources.keys():
                items_to_retrieve[wishlist_key] = self._collect_items(wishlist_key)

        return json.dumps(items_to_retrieve, indent=4)


class WishlistException(Exception):
    """ Generic exception class from which more specific wishlist resource exceptions are derived """


class WishlistNotFoundException(WishlistException):
    """ Raised when a given wishlist resource cannot be found for a specific id """


class WishlistItemNotFoundException(WishlistException):
    """ Raised when a wishlist item is unable to be retrieved """


class WishlistOperationNotPermittedException(WishlistException):
    """ Raised when an operation is deemed to be unacceptable """


class ItemException(Exception):
    """ Generic exception class from which more specific item resource exceptions are derived """


class ItemNotFoundException(ItemException):
    """ Raised when an item cannot be found for a given wishlist """
