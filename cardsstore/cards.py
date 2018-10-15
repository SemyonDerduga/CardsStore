import asyncio
import aiohttp
import string
import random      
import aiofiles
import urllib
import json
import tqdm
class Сards():
        def __init__(self, app):
                self.app = app
        
        def get_cards_names(self):
                with urllib.request.urlopen("https://api.scryfall.com/catalog/card-names") as url:
                        data = json.loads(url.read().decode())
                        return data['data']

        
        async def download_card(self, name):
                async with aiohttp.ClientSession() as session:
                        url = "https://api.scryfall.com/cards/named?exact="+name
                        async with session.get(url) as resp:
                                if resp.status == 200:
                                        data = await resp.json()
                                        image_url=data['image_uris']['normal']
                                        async with session.get(image_url) as response:
                                                if response.status == 200:
                                                        path = self.app['config']['path_images']
                                                        final_path = path+name+'.jpg'
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
                
                card = await self.app['db'].execute('get', 'Card:'+name.lower()+':path')
                
                if card:
                        return card
                else:
                        card = await self.download_card(name)
                        
                        if card:
                                self.app['db'].execute('set', 'Card:'+name.lower()+':path', card.lower())
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

                cards = await self.app['db'].execute('get', 'User:'+username+':cards')
                cards = json.loads(cards)
                cards.append(cardname.lower())
                await self.app['db'].execute('set', 'User:'+username+':cards', json.dumps(cards))

                balance = await self.app['db'].execute('get', 'User:'+username+':balance')
                balance = int(balance.decode("utf-8"))
                balance -= 50 
                self.app['db'].execute('set', 'User:'+username+':balance', balance)
                



#names = get_cards_names()

#coroutines = [download_card(name) for name in names]

#loop = asyncio.get_event_loop()
#loop.run_until_complete(coroutines)
#loop.close()



#@asyncio.coroutine
#def wait_with_progressbar(coros):
#    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
#        yield from f

#names = get_cards_names()

#coro = [download_card(name) for name in names]











#def get_link(name):

 #   with urllib.request.urlopen("https://api.scryfall.com/cards/named?exact="+name) as url:
        #print(url.status)
  #      data = json.loads(url.read().decode())

   #     image_url=data['image_uris']['normal']
    #    return(image_url)
        #img_data = requests.get(image_url).content
        #with open(path+name+'.jpg', 'wb') as handler:
         #   handler.write(img_data)


#cards_names_list = get_cards_names()
#for name in cards_names_list:
#	print(name)
	
#download_card('python')#,'/Users/semenderduga/Desktop/Gathering Watcher/cards/')
