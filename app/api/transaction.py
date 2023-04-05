
from decimal import Decimal

from aiohttp import web
from sqlalchemy import and_

from app.models.transaction_log import NotEnoughMoney
from app.utils import validate_fields_exists_in_dict

from ..models import OperationType, Transaction, TransactionLog, db


async def get_current_user_transaction_handler(request):
    data = await request.json()

    try:
        validate_fields_exists_in_dict(["user_id"], data)
    except ValueError as ve:
        return web.HTTPBadRequest(text=str(ve))

    user_id = data["user_id"]
    async with db.transaction() as _:
        # Лок используется чтобы избежать ситуации,
        # когда два параллельных запроса могут сгенерить несколько идентификаторов транзакции для одного пользователя
        if not (transaction := await Transaction.query.where(
            and_(Transaction.user_id == user_id,
                 Transaction.is_processed == False)  # noqa: E712
        ).with_for_update().gino.first()):
            transaction = Transaction(user_id=user_id)
            await transaction.create()

    return web.json_response({"transaction": transaction.to_dict()})


async def process_transaction_handler(request):
    data = await request.json()

    try:
        validate_fields_exists_in_dict(
            ["user_id", "transaction_id", "type", "amount"], data)
        amount = Decimal(data["amount"])

        async with db.transaction() as _:
            transaction = await Transaction.query.where(
                Transaction.id == data["transaction_id"]).with_for_update().gino.first()
            if transaction.is_processed:
                # Nothing to do
                return web.json_response({}, status=200)
            previous_transaction_log = await TransactionLog.query.order_by(TransactionLog.ts.desc()).gino.first()
            transaction_log, transaction = await TransactionLog.process_transaction(
                OperationType(data["type"]),
                amount,
                transaction,
                previous_transaction_log
            )
            await transaction.update(is_processed=transaction.is_processed).apply()
            await transaction_log.create()
    except NotEnoughMoney as nem:
        return web.HTTPPaymentRequired(text=str(nem))
    except ValueError as ve:
        return web.HTTPBadRequest(text=str(ve))

    return web.json_response({}, status=200)


async def get_transaction_handler(request):
    try:
        validate_fields_exists_in_dict(["id"], request.match_info)
    except ValueError as ve:
        return web.HTTPBadRequest(text=str(ve))
    transaction_id = int(request.match_info["id"])
    transaction = await Transaction.load(log=TransactionLog).where(
        Transaction.id == transaction_id).gino.first()
    return web.json_response({
        "transaction": {"type": transaction.log.operation_type.value, "amount": f"{transaction.log.amount:.2f}"}
    })
