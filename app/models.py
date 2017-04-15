import pickle
from flask import url_for
from werkzeug.exceptions import NotFound
from custom_exceptions import DataValidationError

from datetime import datetime
######################################################################
# Wishlist Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Wishlist(object):
    __redis = None
    UPDATABLE_WISHLIST_FIELDS = ['user_id', 'name']
    UPDATABLE_ITEM_FIELDS = ['description']

    def __init__(self,id=0,name=None,user_id=None):
        """
        Initializes the internal store of wishlist resources.
        """
        self.id = int(id)
        self.name = name
        self.user_id = str(user_id)
        self.created = str(datetime.utcnow())
        self.deleted = False
        self.items = {}

    def self_url(self):
        return url_for('read_wishlist', wishlist_id=self.id, _external=True)

    def save(self):
        if self.name==None:
            raise AttributeError('Name attribute not set!')
        if self.id==0:
            self.id = self.__next_index()
        Wishlist.__redis.set(self.id, pickle.dumps(self.serialize_wishlist()))

    def delete(self):
        Wishlist.__redis.delete(self._index)

    def __next_index(self):
        return Wishlist.__redis.incr('index')

    def serialize_wishlist(self):
        return {"id":self.id, "user_id":self.user_id, "name":self.name, "items":self.items, "created":self.created, "deleted":self.deleted}

    def deserialize_wishlist(self, data):
        try:
            self.name = data['name']
            self.user_id = data['user_id']
        except KeyError as ke:
            raise DataValidationError('Invalid wishlist: missing ' + ke.args[0])
        except TypeError as te:
            raise DataValidationError('Invalid wishlist: body of request contained bad or no data')
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def use_db(redis):
        Wishlist.__redis = redis

    @staticmethod
    def remove_all():
        Wishlist.__redis.flushall()

    @staticmethod
    def all():
        results = []
        for key in Wishlist.__redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Wishlist.__redis.get(key))
                wl = Wishlist(data['id']).deserialize_wishlist(data)
                results.append(wl)
        return results

    @staticmethod
    def find(id):
        if Wishlist.__redis.exists(id):
            data = pickle.loads(Wishlist.__redis.get(id))
            wl = Wishlist(data['id']).deserialize_wishlist(data)
            return wl
        else:
            return None

    @staticmethod
    def find_or_404(id):
        wishlist = Wishlist.find(id)
        if not wishlist:
            raise NotFound("Wishlist with id '{}' was not found".format(id))
        return wishlist