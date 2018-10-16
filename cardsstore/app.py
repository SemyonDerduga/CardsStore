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
import json
import bcrypt

async def create_app(config: dict):
    app = web.Application()
    

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
    app['db'] = await aioredis.create_pool(config['database_uri'])
    setup_security(app, policy, DictionaryAuthorizationPolicy(app['db']))
    app.on_startup.append(on_start)
    
    app.on_cleanup.append(on_shutdown)

    return app

def update_user(app, name, password, balance, cards):
    app['db'].execute('set', 'User:'+name+':password', bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
    app['db'].execute('set', 'User:'+name+':balance', balance)
    app['db'].execute('set', 'User:'+name+':cards', json.dumps(cards))
    

async def on_start(app):
    pass
    #config = app['config']
    update_user(app,'Jack','1',300,['python','cobra'])
    update_user(app,'Sam','1213',1500,['python','cobra'])
    update_user(app,'Test','Test',300,[])




    

async def on_shutdown(app):
    await app['db'].close()
