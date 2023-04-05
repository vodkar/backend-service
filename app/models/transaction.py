from .db import db


class Transaction(db.Model):
    """Сущность используется в основном для генерации уникального идентификатора транзакций.
    Пользователь, получив этот идентификатор может произвести только одну транзакцию.
    Для каждого пользователя может существовать только одна запись с is_process = False.
    Можно добавить триггер на уровне БД на это, чтобы контролировать это
    """
    __tablename__ = "transactions"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    is_processed = db.Column(db.Boolean(), default=False)
