from flask import Flask


#Creating the flask app
app = Flask(__name__)


#Load Configurations
#Make a configuration file!
#app.config.from_object('config')

import server
import models
import custom_exceptions