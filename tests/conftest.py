from pytest import fixture

from app.app import init_app
from app.startups.database import init_db


@fixture
async def app():
    app = init_app()
    return app


@fixture
async def http_client(aiohttp_client, app):
    return await aiohttp_client(app)


@fixture(autouse=True)
async def prepare_db(app):
    await init_db(app)
    await app['db'].gino.create_all()
