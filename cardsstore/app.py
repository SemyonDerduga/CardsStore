from aiohttp import web
from .routes import setup_routes
import jinja2
import aiohttp_jinja2
import aioredis
from cryptography import fernet
import base64
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup as setup_session
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from authz import DictionaryAuthorizationPolicy
from users import user_map
async def create_app(config: dict):
    app = web.Application()
    app.user_map = user_map

    app['config'] = config
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('cardsstore', 'templates')
    )
    setup_routes(app)

    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    
    storage = EncryptedCookieStorage(secret_key, cookie_name='API_SESSION')
    setup_session(app, storage)

    policy = SessionIdentityPolicy()
    setup_security(app, policy, DictionaryAuthorizationPolicy(user_map))

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)

    return app

async def on_start(app):
    config = app['config']
    app['db'] = await aioredis.create_pool(config['database_uri'])

async def on_shutdown(app):
    await app['db'].close()