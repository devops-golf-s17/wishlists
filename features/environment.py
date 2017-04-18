from behave import *
import wishlists
from persistence import db, DatabaseEngine

def before_all(context):
	context.app = wishlists.app.test_client()