from models import *

def get_user_from_username(username_to_search) -> User:
    user = User.query.filter(User.username == username_to_search).first()
    return user

def check_if_user_exists(username_to_search) -> bool:
    user = User.query.filter(User.username == username_to_search).first()
    return user is not None

