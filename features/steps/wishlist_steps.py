from behave import *
import json
from app import server

@given(u'the server is started')
def step_impl(context):
	context.app = server.app.test_client()
	context.server = server
	
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

@then(u'I should see a wishlist with id "{id}"')
def step_impl(context, id):
    assert id in context.resp.data