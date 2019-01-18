# itsdangerous comes along with Flask. Will be used for sending password recovery timed emails
from datetime import datetime
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# We inherit from db.Model to get methods such as .query.get(ID)
# We inherit from flask_login.UserMixin to get certain attributes / methods that flask_login expects.
# To be exact: is_authenticated, is_active, is_anonymous, get_id


class User(db.Model, UserMixin):
    # Define our columns. We note that usernames are between 2 and 20 characters hence the 20 below.
    # We will be taking hashes of usernames / image_file / password, so we can predefine max lengths.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # backref attaches the 'author' attribute Post objects, allowing us to get author info using post.author
    # This means we don't have to do things like User.query.get(post.user_id) to access user info from the ID on a post. It's easier.
    # Lazy defines when SQLalchemy loads the data. True means it will load the data as necessary in one go
    # Notice this is a relationship, not a column, we wouldn't see the post column in a client. This is running an additional query.
    # Note we use an upper-case P in Post because we are referencing the class.
    posts = db.relationship('Post', backref='author', lazy=True)

    # Add a token to allow password reset for user
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    # Takes a token as argument
    # Try to load the token with serializer
    # If exception, didn't work. If no exception, worked, return the user.
    # Note we add the static decorator as no self variables used
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    # Note we are using lower-case u in user. Here we are referencing the table name and column name.
    # Table names are automatically set as lower case.
    # You can set your own table names by setting table name attributes, but we will leave as default
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
