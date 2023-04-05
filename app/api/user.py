import re

import aiohttp
from aiohttp import web

from ..models import User


# function to check that nickname hasn't special symbols
def check_name(name: str) -> bool:
    return bool(re.match(r'^[a-z0-9_]+$', name))


# aiohttp handler for user creation
async def create_user_handler(request):
    data = await request.json()

    if "name" not in data:
        raise aiohttp.web.HTTPBadRequest(text="'name' field is missing")
    
    try:
        user = await User.create_user(name=data["name"])
    except ValueError as ve:
        raise web.HTTPBadRequest(text=str(ve))

    await user.create()
    return web.json_response({'user': user.to_dict()}, status=201)
