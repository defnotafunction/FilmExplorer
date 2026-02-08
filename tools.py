from models import *
from sqlalchemy import select


def get_user_from_username(username_to_search) -> User:
    user = db.session.execute(
        select(User).where(
            User.username == username_to_search
        )
    ).scalar_one()
    return user

def check_if_user_exists(username_to_search) -> bool:
    user = db.session.execute(
        select(User).where(
            User.username == username_to_search
            )).scalar_one_or_none()
    return user is not None

