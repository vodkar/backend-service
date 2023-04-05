from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Tuple

from sqlalchemy import and_

from .db import db
from .transaction import Transaction


# to make tests possible
def get_current_time():
    return datetime.utcnow()


class OperationType(str, Enum):
    WITHDRAW = "WITHDRAW"
    DEPOSIT = "DEPOSIT"


class NotEnoughMoney(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__("Not enough money", *args)


class TransactionLog(db.Model):
    """Проведенные транзакций"""
    __tablename__ = "transaction_logs"
    # имея transaction_id - в качестве ключа избегаем случаев, когда одна транзакция может быть обработана дважды
    transaction_id = db.Column(db.Integer, db.ForeignKey(
        "transactions.id"), primary_key=True)
    operation_type = db.Column(db.Enum(OperationType))
    amount = db.Column(db.Float)
    balance = db.Column(db.Float)
    ts = db.Column(db.DateTime, default=get_current_time)

    @staticmethod
    async def process_transaction(
        operation_type: OperationType,
        amount: Decimal,
        transaction: Optional[Transaction],
        previous_transaction_log: Optional[TransactionLog] = None
    ) -> Tuple[TransactionLog, Transaction]:
        """Проводит транзакцию и возвращает измененные объекты Transaction и TransactionLog"""
        if not transaction:
            raise ValueError("Transaction not exists")
        if transaction.is_processed:
            raise ValueError(
                f"Transaction with id {transaction.id} is already processed")
        if amount <= 0:
            raise ValueError("Amount must be positive and non-zero")

        current_balance: Decimal
        if previous_transaction_log:
            current_balance = Decimal(previous_transaction_log.balance)
        else:
            # no previous transaction, so current balance is 0
            current_balance = Decimal('0.0')

        match operation_type:
            case OperationType.WITHDRAW:
                current_balance -= amount
                if current_balance < 0:
                    raise NotEnoughMoney
            case OperationType.DEPOSIT:
                current_balance += amount
            case _:
                raise ValueError("Unknown operation type")

        transaction_log = TransactionLog(
            transaction_id=transaction.id,
            operation_type=operation_type,
            amount=amount,
            balance=current_balance
        )
        transaction.is_processed = True

        return transaction_log, transaction

    @staticmethod
    async def get_balance(user_id: int, date: Optional[datetime] = None) -> float:
        if date:
            transaction_log = await TransactionLog.load(parent=Transaction).query.where(
                and_(Transaction.user_id == user_id, TransactionLog.ts <= date)
            ).order_by(TransactionLog.ts.desc()).gino.first()
        else:
            transaction_log = await TransactionLog.load(parent=Transaction).query.where(
                Transaction.user_id == user_id).order_by(TransactionLog.ts.desc()).gino.first()
        if transaction_log:
            return Decimal(transaction_log.balance)
        return Decimal(.0)
