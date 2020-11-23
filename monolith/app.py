import os
from flask_googlemaps import GoogleMaps, Map
from monolith.views import blueprints
from monolith.auth import login_manager
from monolith.utilities.gateway_interface import GatewayInterface
from monolith.database import db, User, Restaurant, Booking, Table, Rating
import sys
from flask import Flask
import os
import datetime
import configparser

"""
    The default app configuration: 
    in case a configuration is not found or 
    some data is missing
"""
DEFAULT_CONFIGURATION = {
    "fake_data" : False, # insert some default data in the database (for tests)
    "remove_db" : False, # remove database file when the app starts
    "db_dropall" : False, # remove the record in the database when the app starts

    "wtf_csrf_secret_key" : 'A SECRET KEY',
    "secret_key" : 'ANOTHER ONE'
}


def get_config(configuration=None):
    """
    returns a json file containing the configuration to use in the app

    The configuration to be used can be passed as a parameter, 
    otherwise the one indicated by default in config.ini is chosen

    ------------------------------------
    [CONFIG]
    CONFIG = The_default_configuration
    ------------------------------------

    Params:
        - configuration: if it is a string it indicates the configuration to choose in config.ini
    """
    parser = configparser.ConfigParser()
    if parser.read('config.ini') != []:
        
        if type(configuration) != str: # if it's not a string, take the default one
            configuration = parser["CONFIG"]["CONFIG"]

        print("- GoOutSafe CONFIGURATION:",configuration)
        configuration = parser._sections[configuration] # get the configuration data

        for k,v in DEFAULT_CONFIGURATION.items():
            if not k in configuration: # if some data are missing enter the default ones
                configuration[k] = v

        return configuration
    else:
        return DEFAULT_CONFIGURATION

def create_app(configuration):

    """
    Create the app

    Can receive a string that specifies the configuration to use

    Params:
        -  configuration: if it is a string it indicates the configuration to use, otherwise it is ignored
    """

    app = Flask(__name__)  
    
    configuration = os.getenv("CONFIG", configuration)
    config = get_config(configuration)

    app.config['WTF_CSRF_SECRET_KEY'] = config["wtf_csrf_secret_key"]
    app.config['SECRET_KEY'] = config["secret_key"]
    app.config['SQLALCHEMY_DATABASE_URI'] = config["sqlalchemy_database_uri"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["sqlalchemy_track_modifications"]

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)

    db.create_all(app=app)
    login_manager.init_app(app)

    GoogleMaps(app)
    
    return app

if __name__ == '__main__':
    c = None
    if len(sys.argv) > 1:
        c = sys.argv[1]

    app = create_app(c)
    app.run()
