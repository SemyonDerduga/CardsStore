import aiohttp
from aiohttp_jinja2 import template
import urllib

from textwrap import dedent

from aiohttp import web

from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)

from authz import check_credentials


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
    
    verified = await check_credentials(
        request.app['db'], username, password)
    
    if verified:
        await remember(request, response, username)
        response = web.HTTPFound('/search')
        return response

    return {'message': 'Invalid username / password combination'}

@template('search.html')
async def search_page(request):
    username = await authorized_userid(request)
    
    if username:
        
        balance = await request.app['db'].execute('get', 'User:'+username+':balance')
        balance = balance.decode("utf-8")
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

from ..cards import Сards
import asyncio

@template('card.html')
async def card_view_page(request):
    username = await authorized_userid(request)
    
    if username:
        CardsGetter = Сards(request.app)
        cardname = request.rel_url.query['search_request']
        
        card_path = await asyncio.ensure_future(CardsGetter.get_card(cardname))
        is_owner = await asyncio.ensure_future(CardsGetter.is_owner(username = username, cardname = cardname))

        message = 'Hello, {username}!'.format(username=username)
        
        
        if card_path:
            if not is_owner:
                message += 'Карта '+cardname+' куплена'
                await asyncio.ensure_future(CardsGetter.buy_card(username = username, cardname = cardname))
                
                
        else:
            message += 'Такой карты не существует'
        balance = await request.app['db'].execute('get', 'User:'+username+':balance')
        balance = int(balance.decode("utf-8"))
        message += ' Balance: {balance}'.format(balance=balance)
        return {'message': message, 'path':urllib.parse.quote('file://'+card_path.decode("utf-8")), 'cardname':cardname}
    else:
        response = web.HTTPFound('/')
        return response


