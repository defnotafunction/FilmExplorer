from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username needed!'), Length(min=5)])
    password = PasswordField('Password', validators=[DataRequired('Password needed!'), Length(min=5)])
    submit = SubmitField('Sign in!')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username needed!')])
    password = PasswordField('Password', validators=[DataRequired('Password needed!')])
    submit = SubmitField('Log in!')

class Searchbar(FlaskForm):
    query = StringField('Search!', validators=[DataRequired()])
    search_button = SubmitField('🔍')