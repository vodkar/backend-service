from decimal import getcontext

from aiohttp import web
from aiohttp_middlewares import error_middleware
from environs import Env

from .models import db

app = web.Application(
    middlewares=(
        error_middleware(),
    )
)
app['db'] = db


def init_app() -> web.Application:
    from .api.routes import add_routes
    from .cleanups import close_db
    from .config import Config
    from .startups import init_db

    env = Env()
    env.read_env()

    app['config'] = Config(
        DEBUG=True,
        HOST="localhost",
        PORT=8080,
        DATABASE_URI=f"postgresql://{env('POSTGRES_USER')}:{env('POSTGRES_PASSWORD')}@{env('POSTGRES_HOSTNAME')}/{env('POSTGRES_DB')}")  # noqa: E501

    # Startups
    app.on_startup.append(init_db)

    # Cleanups
    app.on_cleanup.append(close_db)
    add_routes(app)

    # Set decimal precision to 2
    ctx = getcontext()
    ctx.prec = 2

    return app
