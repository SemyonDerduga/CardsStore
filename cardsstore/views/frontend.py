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
        message = 'Вам нужно войти'
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

    return {'message': 'Неправильная комбинация  \n  логина и пароля'}

@template('search.html')
async def search_page(request):
    username = await authorized_userid(request)
    
    if username:
        
        balance = await request.app['db'].execute('get', 'User:'+username+':balance')
        balance = balance.decode("utf-8")
        message = 'Привет, {username}!  \n  Ваш счет: {balance}'.format(
            username=username, balance=balance)
        
        return {'message': message}
    else:
        response = web.HTTPFound('/')
        return response

@template('login.html')
async def logout(request):
    response = web.Response()
    await forget(request, response)
    message = 'Вы вышли   \n  Для продолжения вам нужно войти'
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

        message = 'Привет, {username}!  \n  '.format(username=username)
        
        
        if card_path:
            if not is_owner:
                
                buy = await asyncio.ensure_future(CardsGetter.buy_card(username = username, cardname = cardname))
                if buy:
                    message += 'Карта '+cardname+' куплена\n'
                else:
                    message += 'На вашем счету недостаточно средств!'
                    cardname = 'notfound'


        
        else:
            cardname = 'notfound'
            message += 'Такой карты не существует\n'
        balance = await request.app['db'].execute('get', 'User:'+username+':balance')
        balance = int(balance.decode("utf-8"))
        message += ' Ваш счет: {balance}'.format(balance=balance)
        return {'message': message, 'path':'http://derdu.ga/cards/'+cardname.lower()+'.jpg', 'cardname':cardname}
    else:
        response = web.HTTPFound('/')
        return response


