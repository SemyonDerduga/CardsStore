import aiohttp
import aiofiles
import json


class Сards():
    def __init__(self, app):
        self.app = app
        

    async def download_card(self, name):
        async with aiohttp.ClientSession() as session:
            url = "https://api.scryfall.com/cards/named?exact="+name
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    image_url = data['image_uris']['normal']
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            path = self.app['config']['path_images']
                            final_path = path+name.lower()+'.jpg'
                            f = await aiofiles.open(final_path, mode='wb')
                            await f.write(await response.read())
                            await f.close()
                            return final_path
                        else:
                            return None
                else:
                    return None

    async def get_card(self, name):
        """Return path to card if card exist else return None"""

        card = await self.app['db'].execute('get',
                                            'Card:'+name.lower()+':path')

        if card:
            return card
        else:
            card = await self.download_card(name.lower())

            if card:
                self.app['db'].execute(
                    'set', 'Card:'+name.lower()+':path', card.lower())
                return card
            else:
                return None

    async def is_owner(self, cardname, username):
        """Return True if user is owner card"""
        cards = await self.app['db'].execute('get', 'User:'+username+':cards')
        cards = json.loads(cards)

        if cardname.lower() in cards:
            return True
        else:
            return False

    async def buy_card(self, cardname, username):
        """Add card to user and balance decrement"""
        balance = await self.app['db'].execute('get',
                                               'User:'+username+':balance')
        balance = int(balance.decode("utf-8"))
        if balance-self.app['conf']['request_coast'] < 0:
            return None
        balance -= self.app['conf']['request_coast']
        self.app['db'].execute('set', 'User:'+username+':balance', balance)

        cards = await self.app['db'].execute('get', 'User:'+username+':cards')
        cards = json.loads(cards)
        cards.append(cardname.lower())
        await self.app['db'].execute('set',
                                     'User:'+username+':cards',
                                     json.dumps(cards))
        return True
