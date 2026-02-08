from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username needed!'), Length(min=5)])
    password = PasswordField('Password', validators=[DataRequired('Password needed!'), Length(min=5)])
    submit = SubmitField('Sign up!')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username needed!')])
    password = PasswordField('Password', validators=[DataRequired('Password needed!')])
    submit = SubmitField('Log in!')

class Searchbar(FlaskForm):
    query = StringField('Search!', validators=[DataRequired()])
    search_button = SubmitField('🔍')

class LikeButton(FlaskForm):
    submit = SubmitField('Like')

class RemoveLike(FlaskForm):
    submit = SubmitField('Remove')