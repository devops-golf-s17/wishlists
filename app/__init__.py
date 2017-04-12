from flask import flask


#Creating the flask app
application = Flask(__name__)


#Load Configurations
#Make a configuration file!
#app.config.from_object('config')

import server
import models
import custom_exceptions