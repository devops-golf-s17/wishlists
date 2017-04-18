import pickle
from flask import url_for
from werkzeug.exceptions import NotFound
from custom_exceptions import DataValidationError, ItemNotFoundException
import json
from datetime import datetime
import pickle
######################################################################
# Wishlist Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Wishlist(object):
	__redis = None
	UPDATABLE_WISHLIST_FIELDS = ['user_id', 'name']
	UPDATABLE_ITEM_FIELDS = ['description']
	def __init__(self,id=0,name=None,user_id=None,items={}):
		"""
		Initializes the internal store of wishlist resources.
		"""
		self.id = int(id)
		self.name = name
		self.created = str(datetime.utcnow())
		self.user_id = str(user_id)
		self.items = {}
		self.deleted = False

	def self_url(self):
		return url_for('read_wishlist', wishlist_id=self.id, _external=True)

	def save_wishlist(self):
		if self.id==0:
			self.id = self.__next_index()
		Wishlist.__redis.set(self.id, pickle.dumps(self.serialize_wishlist()))

	def save_item(self):
		Wishlist.__redis.set(self.id, pickle.dumps(self.serialize_wishlist()))

	def all_items(self):
		return self.items

	def find_item(self, item_id):
		temp_items = self.items
		return_item = None
		for key,value in temp_items.iteritems():
			if item_id == value['item_id']:
				return_item = temp_items[key]
		if return_item:
			return return_item
		else:
			raise ItemNotFoundException

	def update_item(self, data):
		temp_items = self.items
		update_item = None
		for key,value in temp_items.iteritems():
			if data['id'] == value['item_id']:
				update_item = temp_items[key]
		if update_item:
			update_item['description'] = data['description']
			self.items = temp_items
			return self.serialize_wishlist()
		else:
			raise ItemNotFoundException

	def remove_item(self, item_id):
		temp_items = self.items
		remove_item = None
		for key,value in temp_items.iteritems():
			if item_id == value['item_id']:
				remove_item = temp_items[key]
				remove_key = key
		if remove_item:
			del temp_items[remove_key]
			self.items = temp_items
		else:
			raise ItemNotFoundException


	def delete(self):
		Wishlist.__redis.delete(self.id)

	def __next_index(self):
		return Wishlist.__redis.incr('index')

	def serialize_wishlist(self):
		return {"id":self.id, "user_id":self.user_id, "name":self.name, "items":self.items, "created":self.created, "deleted":self.deleted}

	def serialize_wishlist_items(self):
		return {"id":self.id, "user_id":self.user_id, "name":self.name, "items":self.items, "created":self.created, "deleted":self.deleted}

	def deserialize_wishlist_items(self,data):
		try:
			self.name = self.name
			self.user_id = self.user_id
			temp_items = self.items
			if not temp_items:
				temp_items[1] = {'item_id':data['id'], 'description':data['description']}
			else:
				if data['id'] not in temp_items.values():
					size = len(temp_items) + 1
					temp_items[size] = {'item_id':data['id'], 'description':data['description']}
					self.items = temp_items
			self.created = self.created
			self.deleted = self.deleted
		except KeyError as ke:
			raise DataValidationError('Invalid wishlist: missing ' + ke.args[0])
		except TypeError as te:
			raise DataValidationError('Invalid wishlist: body of request contained bad or no data')
		return self

	def deserialize_wishlist(self, data):
		try:
			self.name = data['name']
			self.user_id = data['user_id']
			if 'items' not in data:
				self.items = {}
			else:
				self.items = data['items']
			self.created = str(datetime.utcnow())
			self.deleted = self.deleted
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
				data = Wishlist.__redis.get(key)
				pickled_data = pickle.loads(data)
				wl = Wishlist(pickled_data['id']).deserialize_wishlist(pickled_data)
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
