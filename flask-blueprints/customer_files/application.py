# from pprint import pprint

from itsdangerous import URLSafeTimedSerializer
from flask.ext.login import LoginManager
from flask.ext.assets import Bundle

from wdft import create_app as create_base_app
from coastal.views.main.views import main_blueprint
from coastal.views.admin.views import admin_blueprint
from coastal.views.api.views import api_blueprint

from coastal.database.database import db_session
from coastal.models.admin import User
from .cache import cache

def create_app():

    app = create_base_app([main_blueprint, admin_blueprint, api_blueprint])

    from coastal.settings import config

    app.config.from_object(config)
    login_serializer = URLSafeTimedSerializer(app.secret_key)

    # cache config
    cache.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "/coastal/admin/login"

    login_manager.init_app(app)

    # the user loader for flask-login
    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(int(userid))

    @login_manager.token_loader
    def load_token(token):
        """
        Flask-Login token_loader callback. 
        The token_loader function asks this function to take the token that was 
        stored on the users computer process it to check if its valid and then 
        return a User Object if its valid or None if its not valid.
        """
        max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
        #Decrypt the Security Token, data = [username, hashpass]
        data = login_serializer.loads(token, max_age=max_age)
        #Find the User
        user = User.query.filter_by(id=data[0]).first()

        #Check Password and return user or None
        if user and data[1] == user.password:
            return user
        return None


    # login_manager.refresh_view = "coastal_admin.login"

    # This clears the db session if there are any errors in the request.
    # VERY IMPORTANT
    @app.teardown_request
    def shutdown_session(response):
        db_session.remove()
        return response

    return app
