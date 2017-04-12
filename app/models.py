from flask import url_for
from werkzeug.exceptions import NotFound
from custom_exceptions import DataValidationError
import json
from datetime import datetime


class Wishlist(object):
    """
    Simple class for a persistence layer interface that uses a dict as 
    its internal store.  Each entry in the dict is another dict that
    acts as an individual "wishlist resource".
    """

    UPDATABLE_WISHLIST_FIELDS = ['user_id', 'name']
    UPDATABLE_ITEM_FIELDS = ['description']
    __redis = None

    def __init__(self,_index=0,name=None,user_id=0):
        """
        Initializes the internal store of wishlist resources.
        """
        self._index = int(_index)
        self.name = name
        self.user_id = str(user_id)
        self.products = {}
        self.created = str(datetime.utcnow())
        self.deleted = False
        self.items = {}

    
    def self_url(self):
    	return url_for('read_wishlist', wishlist_id=self.id, _external=True)

    def save(self):
    	if self.name==None:
    		raise AttributeError('Name attribute not set!')
    	if self._index==0:
    		self._index = self.__next_index()
    	Wishlist.hmset(self._index, self.serialize())
    
    def __next_index(self):
    	return Wishlist.__redis.incr('index')

    def serialize(self):
    	return {"created":self.created, "user_id":self.user_id, "deleted": self.deleted, "id":self._index, "name":self.name, "items":self.items}			

    def delete(self):
    	Wishlist.__redis.delete(self._index)

    def deserialize(self, data):
    	try:
    		self.name = data['name']
    		self.user_id = data['user_id']
    		self.deleted = data['deleted']
    		self.created = data['created']
    		self.items = data['items']
    	except KeyError as ke:
    		raise DataValidationError('Invalid wishlist: missing ' + ke.args[0])
    	except TypeError as te:
    		raise DataValidationError('Invalid wishlist: body of request contained bad or no data')
    	return self


######################################################################
#  S T A T I C   D A T A B A S E   M E T H O D S
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
			if key!= 'index':
				data = Wishlist.__redis.hgetall(key)
				wishlist = Wishlist(data['id']).deserialize(data)
				results.append(wishlist)
		return results
	
	@staticmethod
	def find(id):
		if Wishlist.__redis.exists(id):
			data = Wishlist.__redis.hgetall(id)
			wishlist = Wishlist(data['id']).deserialize(data)
			return wishlist
		else:
			return None

	@staticmethod
	def find_or_404(id):
		wishlist = Wishlist.find(id)
		if not wishlist:
			raise NotFound("Wishlist with id '{}' was not found".format(id))
		return wishlist

										
