import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
    # Randomize image name to avoid naming collisions
    random_hex = secrets.token_hex(8)
    # form_picture will look like form.picture.data, which has the attribute filename
    # os.path.splitext splits picture.jpg into picture and jpg
    _, f_ext = os.path.splitext(form_picture.filename)
    # Define filename by concatenation of hex and filename
    picture_file = random_hex + f_ext
    # Get the path to store
    picture_path = os.path.join(current_app.root_path, 'static', 'profile_pics', picture_file)
    # Resize and save out the picture
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    # Return the file name to use in setting DB value
    return picture_file


def send_reset_email(user):
    # The get_reset_token custom method returns a token that expires after 1800 seconds default
    token = user.get_reset_token()
    # Be careful to not spoof a sender or you will end up in spam folder.
    # Have something that is coming from your domain or your email address
    msg = Message('Password Reset Request',
                  sender='user@demo.com',
                  recipients=[user.email])

    # We use a multi-line string here to compose the message.
    # Note that the multi-line string will take in the python-esque tabs, so we remove these.
    # The _external=True parameter makes sure we return absolute URL, not relative URL [default, fine within app]
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
