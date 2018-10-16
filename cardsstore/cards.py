import aiohttp
import aiofiles
import json
import os


class Сards():
    def __init__(self, app):
        self.app = app

    async def download_card(self, name):
        """Download the card if it exists and return path, else return None"""
        name = name.lower().replace(" ", "")
        async with aiohttp.ClientSession() as session:
            url = "https://api.scryfall.com/cards/named?exact="+name
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                image_url = data["image_uris"]["normal"]
                async with session.get(image_url) as response:
                    if response.status != 200:
                        return None
                    path = self.app["config"]["path_images"]
                    final_path = os.path.join(path, name.lower()+".jpg")
                    f = await aiofiles.open(final_path, mode="wb")
                    await f.write(await response.read())
                    await f.close()
                    return final_path

    async def get_card(self, name):
        """Return path to the card if the card exists"""
        name = name.lower().replace(" ", "")
        card = await self.app["db"].execute("get",
                                            "Card:"+name+":path")

        if card:
            return card
        else:
            card = await self.download_card(name)

            if card:
                self.app["db"].execute(
                    "set", "Card:"+name+":path", card.lower())
                return card
            else:
                return None

    async def is_owner(self, cardname, username):
        """Return True if the user owns the card"""
        cards = await self.app["db"].execute("get", "User:"+username+":cards")
        cards = json.loads(cards)

        return cardname.lower().replace(" ", "") in cards

    async def buy_card(self, cardname, username):
        """Add a card to the user and reduce the balance"""

        request_coast = int(self.app["config"]["request_coast"])

        balance = await self.app["db"].execute("get",
                                               "User:"+username+":balance")
        balance = int(balance.decode("utf-8"))

        if balance - request_coast < 0:
            return None
        balance -= request_coast
        self.app["db"].execute("set", "User:"+username+":balance", balance)

        cards = await self.app["db"].execute("get", "User:"+username+":cards")
        cards = json.loads(cards)
        cards.append(cardname.lower().replace(" ", ""))
        await self.app["db"].execute("set",
                                     "User:"+username+":cards",
                                     json.dumps(cards))
        return True
