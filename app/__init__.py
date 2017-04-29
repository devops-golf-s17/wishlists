from flask import Flask


#Creating the flask app
app = Flask(__name__)



app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "DevOps e-Commerce Wishlists App",
            "description": "This is a Wishlists server with Redis.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

#Load Configurations
#Make a configuration file!
#app.config.from_object('config')

import server
import models
import custom_exceptions