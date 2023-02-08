from gino import Gino

db = Gino()


class User(db.Model):
    balance = db.Column(...)
    ...


class Transaction(db.Model):
    ...
