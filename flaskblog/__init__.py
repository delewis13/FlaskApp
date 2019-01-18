from flaskblog.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


# Create our db with SQLAlchemy. We can represent our database structures as classes
# These classes are called models. Each class will be its own table in the database
db = SQLAlchemy()

# Using flask-bcrypt installed with pip to manage password hashing
bcrypt = Bcrypt()

# Using flask-login installed with pip to manage logins
# We use .login_view of whatever our redirect needs to be. In this case, 'login' function is within users blueprint.
# Login_view determines our redirects if we fail our @login_required decorator
# Login_message_category adds classes to our flash messages [bootstrap: info]
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

# Setup mailing ability
mail = Mail()


def create_app(config_class=Config):
    # Note: We don't bring the extensions into this create_app function
    # This is so that the extension object is not initially bound to the app
    # Using this design pattern no application specific state is stored on the extension object
    # Thus one extension object can be used for multiple apps
    # Note: if we run this file directly, __name__ = '__main__'.
    # If we run from run.py, __name__ = 'flaskblog'
    app = Flask(__name__)

    # Initialise all configuration for app
    app.config.from_object(Config)

    # Initialise all our extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # We do this at the end to avoid circular importes with the routes.py file, which relies on importing app
    # We have established blueprints for all our routes so we import those
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
