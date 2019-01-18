# pip install flask-wtf for both of these packages
# For a refresher on construction of this page checkout:
# https://www.youtube.com/watch?v=UIJKdCIEXUQ&index=3&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
# Python Flask Tuotial: Full-Featured Web App Part 3

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
