from behave import *
import json
from app import server

@given(u'the server is started')
def step_impl(context):
	context.app = server.app.test_client()
	context.server = server

@given(u'the following wishlists')
def step_impl(context):
    server.data_reset()
    for row in context.table:
    	server.data_load_wishlist({"name": row['name'], "id": row['id'], "user_id": row['user_id']})

@given(u'the following items')
def step_impl(context):
	for row in context.table:
		server.data_load_wishlist_items({"id": row['item_id'], "wishlist_id": row['wishlist_id'], "description": row['description']})	

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

@when(u'I visit "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200


@when(u'I retrieve "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = '/{}/{}'.format(url, id)
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@then(u'I should see a wishlist with id "{id}"')
def step_impl(context, id):
    assert id in context.resp.data


@then(u'I should see "{message}" in this wishlist')
def step_impl(context, message):
    assert message in context.resp.data
