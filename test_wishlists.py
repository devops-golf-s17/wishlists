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
		resp = self.app.get('/wishlists/1')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['user_id'], 'palak')

	def test_read_wishlist_not_found(self):
		resp = self.app.get('/wishlists/2')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_item(self):
		resp = self.app.get('/wishlists/1/items')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(resp.data) > 0)

	def test_item_not_found(self):
		resp = self.app.get('/wishlists/2/items')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_read_wishlist_item(self):
		resp = self.app.get('/wishlists/1/items/item1')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['description'], 'test item 1')

	def test_read_wishlist_item_item_not_found(self):
		resp = self.app.get('/wishlists/1/items/item2')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_read_wishlist_item_wishlist_not_found(self):
		resp = self.app.get('/wishlists/2/items/item2')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

if __name__ == '__main__':
	unittest.main()
