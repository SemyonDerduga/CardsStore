from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_security import (
    remember, forget, authorized_userid,
)
from authz import check_credentials
from ..cards import Сards
import asyncio
from os import path


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

        balance = await request.app['db'].execute('get',
                                                  'User:'+username+':balance')
        balance = balance.decode("utf-8")

        return {'name': username,
                'balance': balance}
    else:
        response = web.HTTPFound('/')
        return response


@template('login.html')
async def logout(request):
    response = web.Response()
    await forget(request, response)
    message = 'Вы вышли   \n  Для продолжения вам нужно войти'
    return {'message': message}


@template('card.html')
async def card_view_page(request):
    username = await authorized_userid(request)

    if not username:
        response = web.HTTPFound('/')
        return response

    card_manager = Сards(request.app)
    cardname = request.rel_url.query['search_request']

    card_path = await asyncio.ensure_future(
        card_manager.get_card(cardname))
    is_owner = await asyncio.ensure_future(
        card_manager.is_owner(username=username, cardname=cardname))

    if card_path:
        status = 'Ваша карта уже приобретена'
        if not is_owner:
            buy = await asyncio.ensure_future(
                card_manager.buy_card(username=username,
                                      cardname=cardname))
            if buy:
                status = 'Карта '+cardname+' куплена'
            else:
                status = 'На вашем счету недостаточно средств!'
                cardname = 'notfound'

    else:
        cardname = 'notfound'
        status = 'Такой карты не существует'

    balance = await request.app['db'].execute('get',
                                              'User:'+username+':balance')
    balance = int(balance.decode("utf-8"))

    return {'name': username,
            'balance': balance,
            'status': status,
            'path': path.join(request.app['config']['get_cards_url'],
                              cardname.lower().replace(" ", "")+'.jpg'),
            'cardname': cardname}
