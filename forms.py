from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class SignUpForm(FlaskForm):
    """
    Form used on the signup page. Used to create accounts.
    """
    username = StringField('Username', validators=[DataRequired('Username needed!'), Length(min=5)])
    password = PasswordField('Password', validators=[DataRequired('Password needed!'), Length(min=5)])
    submit = SubmitField('Sign up!')

class LoginForm(FlaskForm):
    """
    Form used on the login page. Used to log into accounts.
    """
    username = StringField('Username', validators=[DataRequired('Username needed!')])
    password = PasswordField('Password', validators=[DataRequired('Password needed!')])
    submit = SubmitField('Log in!')

class Searchbar(FlaskForm):
    """
    Form used to search items up based on the query.
    """
    query = StringField('Search!', validators=[DataRequired()])
    search_button = SubmitField('🔍')

class LikeButton(FlaskForm):
    """
    Like form. Add media to your liked media list.
    """
    submit = SubmitField('Like')

class RemoveLike(FlaskForm):
    """
    RemoveLike form. Used to remove media from a user's liked list.
    """
    submit = SubmitField('Remove')