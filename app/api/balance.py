from datetime import datetime

from aiohttp import web

from app.utils import validate_fields_exists_in_dict

from ..models.transaction_log import TransactionLog


async def get_current_balance_handler(request: web.Request):
    try:
        validate_fields_exists_in_dict(["id"], request.match_info)
    except ValueError as ve:
        return web.HTTPBadRequest(text=str(ve))

    user_id = int(request.match_info["id"])
    if date := request.query.get("date"):
        date = datetime.fromisoformat(date)
        balance = await TransactionLog.get_balance(user_id, date)
    else:
        balance = await TransactionLog.get_balance(user_id)

    return web.json_response({"balance": f'{balance:.2f}'})
