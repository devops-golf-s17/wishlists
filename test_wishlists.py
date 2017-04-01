 #Test cases can be run with either of the following:
 #python -m unittest discover
 #nosetests -v --rednose --nologcapture

import json
import unittest
import logging
import wishlists
from persistence import db, DatabaseEngine
from flask_api import status

class WishlistTestCase(unittest.TestCase):
	def setUp(self):
		wishlists.db.create_wishlist('wl1','user1')
		wishlists.db.add_item(1, {'id' : 'item1', 'description' : 'test item 1'})
		self.db = wishlists.db
		self.app = wishlists.app.test_client()

	def tearDown(self):
		wishlists.db=DatabaseEngine()

	def test_update_wishlist(self):
		new_wl = {'name': 'wl2', 'user_id': 'user2'}
		data = json.dumps(new_wl)
		resp = self.app.put('/wishlists/1', data=data, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_200_OK )
		new_json = json.loads(resp.data)
		self.assertEqual (new_json['name'], 'wl2')
		self.assertEqual (new_json['user_id'], 'user2')

	def test_update_wishlist_with_no_data(self):
		resp = self.app.put('/wishlists/1', data=None, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

	def test_update_wishlist_with_text_data(self):
		resp = self.app.put('/wishlists/1', data="hello", content_type='text/plain')
		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

	def test_update_wishlist_with_no_name(self):
		new_wl = {'user_id': 'user2'}
		data = json.dumps(new_wl)
		resp = self.app.put('/wishlists/1', data=data, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

	def test_update_wishlist_with_no_user_ID(self):
		new_wl = {'name': 'wl2'}
		data = json.dumps(new_wl)
		resp = self.app.put('/wishlists/1', data=data, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

	def test_update_wishlist_not_found(self):
		new_wl = {'name': 'wl2', 'user_id': 'user2'}
		data = json.dumps(new_wl)
		resp = self.app.put('/wishlists/2', data=data, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )

if __name__ == '__main__':
	unittest.main()
