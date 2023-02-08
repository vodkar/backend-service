from aiohttp import web


async def create_user(request):
    ...
    return web.json_response({
        'id': ...,
        'name': ...,
    })


def add_routes(app):
    app.router.add_route('GET', r'/v1/user', create_user, name='create_user')
    app.router.add_route('POST', r'/v1/user/{id}/balance', get_user_balance, name='get_user')
    app.router.add_route('PUT', r'/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', r'/v1/transaction/{id}', get_transaction, name='incoming_transaction')
    ...
