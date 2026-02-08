from flask_wtf import FlaskForm
from models import User, Media
from extensions import db
from sqlalchemy import select

def safe_db_add(obj):
    try:
        db.session.add(obj)
        db.session.commit()
    except Exception:
        db.session.rollback() 

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


