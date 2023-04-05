from .balance import get_current_balance_handler
from .transaction import get_current_user_transaction_handler, get_transaction_handler, process_transaction_handler
from .user import create_user_handler


def add_routes(app):
    app.router.add_route('POST', r'/v1/user',
                         create_user_handler, name='create_user')
    app.router.add_route(
        'GET', r'/v1/user/{id}/balance', get_current_balance_handler, name='get_user_balance')
    app.router.add_route('PUT', r'/v1/transaction',
                         process_transaction_handler, name='add_transaction')
    app.router.add_route(
        'GET', r'/v1/transaction/{id}', get_transaction_handler, name='incoming_transaction')
    # По хорошему этот метод должен быть 'GET' но так как у нас нет идентификации через,
    # например, jwt token, то пришлось сделать 'POST'
    app.router.add_route('POST', r'/v1/transaction',
                         get_current_user_transaction_handler, name='get_current_user_transaction')
