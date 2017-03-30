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
		wishlists.app.debug = True
		wishlists.app.logger.addHandler(logging.StreamHandler())
		wishlists.app.logger.setLevel(logging.CRITICAL)
		wishlists.db.create_wishlist('wl1','palak')
		wishlists.db.add_item(1, {'id' : 'item1', 'description' : 'test item 1'})
		self.db = wishlists.db
		self.app = wishlists.app.test_client()

	def tearDown(self):
		wishlists.db=DatabaseEngine()

#	def test_add_wishlist(self):
#		wishlist_count = len(self.db._wishlist_resources)
#		new_wl = {'name' : 'wl2', 'user_id' : 'palak'}
#		data = json.dumps(new_wl)
#		resp = self.app.post('/wishlists', data=data, content_type='application/json')
#		self.assertEqual(status.HTTP_201_CREATED, resp.status_code)

	def test_update_wishlist(self):
		new_wl = {'name': 'wl2', 'user_id': 'pala'}
		data = json.dumps(new_wl)
		resp = self.app.put('/wishlists/1', data=data, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_200_OK )
		new_json = json.loads(resp.data)
		self.assertEqual (new_json['user_id'], 'pala')

	def test_update_item(self):
		new_wl = {'description' : 'updated'}
		data = json.dumps(new_wl)
		resp = self.app.put('/wishlists/1/items/item1', data=data, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_200_OK )
		#print resp
		new_json = json.loads(resp.data)
		#print new_json
		self.assertEqual (new_json['items']['item1']['description'], 'updated')

	def test_update_wishlist_with_no_data(self):
		resp = self.app.put('/wishlists/1', data=None, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

	def test_update_item_with_no_data(self):
		resp = self.app.put('/wishlists/1/items/item1', data=None, content_type='application/json')
		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )


#	def test_update_wishlist_with_text_data(self):
#		resp = self.app.put('/wishlists/1', data="hello", content_type='text/plain')
#		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

#	def test_update_item_with_text_data(self):
#		resp = self.app.put('/wishlists/1', data="hello", content_type='text/plain')
#		self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )

if __name__ == '__main__':
	unittest.main()
