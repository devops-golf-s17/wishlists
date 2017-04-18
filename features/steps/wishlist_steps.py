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

@given(u'the following wishlists')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the following wishlists')

@given(u'the following items')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the following items')

	
