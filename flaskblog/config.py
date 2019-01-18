import os


class Config:
    # Need a secret key to prevent modifying cookies, cross-site forgery attacks etc.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database. Note we use ///. For sqllite, this means we are specifying a relative path.
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    # Configure mailing parameters
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
