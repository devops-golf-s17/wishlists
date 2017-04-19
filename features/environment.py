from behave import *
import sys
sys.path.insert(0, '/vagrant/')
from app import server
def before_all(context):
	context.app = server.app.test_client()
	server.initialize_redis()
	context.server = server
