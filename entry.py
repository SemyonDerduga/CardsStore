import asyncio
import aiohttp
import argparse
import aioreloader
from cardsstore import create_app

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    print("Library uvloop is not available")


parser = argparse.ArgumentParser(description="Cards Store")
parser.add_argument('--host', help="Host to listen",default="0.0.0.0")
parser.add_argument('--port', help="Port to connections",default="8080")
parser.add_argument('--reload', action="store_true",
                    help="Autoreload code on change")

args = parser.parse_args()

app = create_app()

if args.reload:
    print("Start with reload code")
    aioreloader.start()

if __name__ == '__main__':
    aiohttp.web.run_app(app, host=args.host, port=args.port)
