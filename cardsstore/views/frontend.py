import aiohttp
from aiohttp_jinja2 import template


from textwrap import dedent

from aiohttp import web

from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)

from authz import check_credentials

# @template('index.html')
# async def index(request):
#    await request.app['db'].execute('set', 'UserName', 'Sam')
#    name = await request.app['db'].execute('get', 'UserName')
#    name = name.decode("utf-8")
#    site_name = request.app['config'].get('site_name')
#    return {'site_name':site_name,'name':name}


# index_template = dedent("""
#    <!doctype html>
#        <head></head>
#        <body>
#            <p>{message}</p>
#            <form action="/login" method="post">
#                Login:
#                <input type="text" name="username">
#                Password:
#                <input type="password" name="password">
#                <input type="submit" value="Login">
#            </form>
#            <a href="/logout">Logout</a>
#        </body>
# """)

@template('login.html')
async def index(request):
    username = await authorized_userid(request)
    
    if username:
        response = web.HTTPFound('/search')
        return response
    else:
        message = 'You need to login'
        return {'message': message}


@template('login.html')
async def login(request):
    response = web.HTTPFound('/')
    form = await request.post()
    username = form.get('username')
    password = form.get('password')
    # return {'message':(username+' '+password)}
    verified = await check_credentials(
        request.app.user_map, username, password)
    if verified:
        await remember(request, response, username)
        response = web.HTTPFound('/search')
        return response

    return {'message': 'Invalid username / password combination'}

@template('search.html')
async def search_page(request):
    username = await authorized_userid(request)
    
    if username:
        balance = list(request.app.user_map[username])[2]
        message = 'Hello, {username}! \n Balance: {balance}'.format(
            username=username, balance=balance)
        return {'message': message}
    else:
        response = web.HTTPFound('/')
        return response

@template('login.html')
async def logout(request):
    response = web.Response()
    await forget(request, response)
    message = 'You have been logged out\nYou need to login'
    return {'message': message}

@template('card.html')
async def card_view_page(request):
    username = await authorized_userid(request)
    
    if username:
        balance = list(request.app.user_map[username])[2]
        message = 'Hello, {username}! \n Balance: {balance}'.format(
            username=username, balance=balance)
        return {'message': message}
    else:
        response = web.HTTPFound('/')
        return response