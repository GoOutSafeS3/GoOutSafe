from flask_googlemaps import GoogleMaps
from monolith.views import blueprints
from monolith.auth import login_manager
from monolith.utilities import filters
from flask import Flask


WTF_CSRF_SECRET_KEY = "A KEY"
SECRET_KEY = "ANOTHER KEY"

def create_app():

    """
    Create the app

    Can receive a string that specifies the configuration to use

    """

    app = Flask(__name__)  


    app.config['WTF_CSRF_SECRET_KEY'] = WTF_CSRF_SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    login_manager.init_app(app)

    GoogleMaps(app)

    filters.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
