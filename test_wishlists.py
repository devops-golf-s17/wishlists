# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import json
import unittest
import logging
import wishlists
from persistence import db, DatabaseEngine
from flask_api import status

class WishlistTestCase(unittest.TestCase):
	def setUp(self):
		wishlists.db.create_wishlist('wl1','palak')
		wishlists.db.add_item(1, {'id' : 'item1', 'description' : 'test item 1'})
		self.db = wishlists.db
		self.app = wishlists.app.test_client()

	def tearDown(self):
		wishlists.db=DatabaseEngine()

	def test_wishlists(self):
		resp = self.app.get('/wishlists')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(resp.data) > 0)

	def test_read_wishlist(self):
		resp = self.app.get('/wishlists/wl1')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['user_id'], 'palak')

	def test_read_wishlist_not_found(self):
		resp = self.app.get('/wishlists/wl2')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_item(self):
		resp = self.app.get('/wishlists/wl1/items')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(resp.data) > 0)

	def test_item_not_found(self):
		resp = self.app.get('/wishlists/wl2/items')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_read_wishlist_item(self):
		resp = self.app.get('/wishlists/wl1/items/item1')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['description'], 'test item 1')

	def test_read_wishlist_item_item_not_found(self):
		resp = self.app.get('/wishlists/wl1/items/item2')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_read_wishlist_item_wishlist_not_found(self):
		resp = self.app.get('/wishlists/wl2/items/item2')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	"""
		Working test case.
		This is a test case to check whether a wishlist is created or not.
		POST verb checked here.
	"""
	def test_create_wishlist(self):
		new_wishlist = {'name':'xynazog','user_id':'123'}
		data = json.dumps(new_wishlist)
		resp = self.app.post('/wishlists',data=data,content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		new_json = json.loads(resp.data)
		self.assertEqual(new_json['name'],'xynazog')

	"""
		Working test case.
		This is a test case to check whether an item is added to a wishlist or not.
		POST verb is checked here.
	"""
	def test_create_wishlist_item(self):
		new_wishlist = {'name':'xynazog','user_id':'123'}
		dataOne = json.dumps(new_wishlist)
		self.app.post('/wishlists',data=dataOne,content_type='application/json')
		new_item = {'id':'item3','description':'test item 3'}
		data = json.dumps(new_item)
		resp = self.app.post('/wishlists/1/items',data=data,content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		new_json = json.loads(resp.data)
		self.assertEqual(new_json['id'],'item3')

	"""
		Not working test case.
		This is a test case to check whether an item is added to a wishlist out of index.
		POST verb is checked here.
	"""
	def test_create_wishlist_item_wishlist_not_found(self):
		new_item = {'id':'item3','description':'test item 3'}
		data = json.dumps(new_item)
		resp = self.app.post('/wishlists/3/items',data=data,content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


if __name__ == '__main__':
	unittest.main()
