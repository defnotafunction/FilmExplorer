from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, index=True)
    hashed_password = db.Column(db.String(150))
    liked_media = db.relationship("Media", backref='user', cascade="all, delete-orphan") 

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    media_type = db.Column(db.String)