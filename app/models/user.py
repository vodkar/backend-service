import re

from .db import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode())

    @staticmethod
    async def create_user(name: str):
        name = name.lower()
        if not re.match(r'^[a-z0-9_]+$', name):
            raise ValueError("a-z0-9_ are only available characters for name")
        if await User.query.where(User.name == name).gino.first():
            raise ValueError("User with this name already exists")
        return User(name=name)
    
        