from flask_wtf import FlaskForm
from models import User, Media
from extensions import db
from sqlalchemy import select

def safe_db_add(obj) -> None:
    """
    Safely adds to the database and commits using a try and except block.
    
    :param obj: Column to add to the database.
    :type obj: SQLAlchemy.Column.
    """
    try:
        db.session.add(obj)
        db.session.commit()
    except Exception:
        db.session.rollback() 

def get_user_from_username(username_to_search: str) -> User:
    """
    Returns the User object that has the username "username_to_search".
    
    :param username_to_search: The username used to search for a user.
    :return: User object.

    """
    user = db.session.execute(
        select(User).where(
            User.username == username_to_search
        )
    ).scalar_one()
    return user

def check_if_user_exists(username_to_search: str) -> bool:
    """
    Returns True if a user with the username "username_to_search" exists, otherwise returns False.
    
    :param username_to_search: The username used to search for a user.
    :return: True or False.
    """

    user = db.session.execute(
        select(User).where(
            User.username == username_to_search
            )).scalar_one_or_none()
    
    return user is not None

def check_media_obj_in_user_liked(media_id: int, user_obj) -> bool:
    """
    Returns a bool based on if a media object (identified by it's id) is in user's liked titles.
    
    :param media_id: The id of the media object.
    :param user_obj: The user object that is going to have their "liked_media" attribute checked.
    :type user_obj: SQLAlchemy.Column.
    :return: Returns True if a media object is in user_obj's liked media else False.
    """
    return any(media.media_id == media_id for media in user_obj.liked_media)

def get_users_from_query(query: str) -> list[User]:
    """
    Returns a bool based on if a media object (identified by it's id) is in user's liked titles.
    :param query: The text used to fetch users with similar usernames.
    :return: Returns True if a media object is in user_obj's liked media else False
    """
    fetched_users = db.session.execute(
        select(User).where(User.username.contains(query))
    ).scalars().all()
    return fetched_users