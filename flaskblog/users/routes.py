# PIL comes from pip install Pillow
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create hashed password, create user object, add to DB, commit to DB
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # We use the 3.6 string formating f'blah blah {var_name} blah blah'
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Get the user from the database, then check if a user was returned and if they gave the right password
        # user.password is the hashed password from DB, form.password.data is their entered password.
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Login_user from flask_login package.
            # Takes a remember attribute to deal with sessions.
            login_user(user, remember=form.remember.data)
            # Get the query parameter if exists. Use this for appropriate redirect.
            # If redirected to login via @login_required decorator, then previous page name will be query param
            # Note: request.args is a dict, use .get('next') not ['next'] so we don't error if no result
            next_page = request.args.get('next')
            flash('Login Successful', 'success')
            # Now redirect based on if we got a query parameter previously.
            # Note that we don't use url_for(next_page), as next_page = '/blah', but url_for would need 'blah' [function name]
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        # SQLalchemy allows you to just change the current_user and submit that to change DB details
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.image_file = picture_file
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/home/<string:username>")
def user_posts(username):
    # Determine our page number from query string
    page = request.args.get('page', 1, type=int)
    # Get our user from the database
    user = User.query.filter_by(username=username).first_or_404()
    # Sort posts by newest to oldest, then paginate them. Use the \ to break over multiple lines
    # Alternatively could use parentheses around entire query string.
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=4)

    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        flash('You must be logged out before resetting password', 'info')
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'An email has been sent with password reset instructions to the email {user.email}', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('You must be logged out before resetting password', 'info')
        return redirect(url_for('main.home'))
    # We added the custom method verify_reset_token to User model
    # Let's use this. We pass in a token, if valid returns user, if invalid returns none
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        # Create hashed password, edit the user to reflect new password, commit to DB
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        # We use the 3.6 string formating f'blah blah {var_name} blah blah'
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
