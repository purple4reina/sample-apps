import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import sys
sys.path.append('..')

from utils.decorators import print_nice_transaction_trace

import aiohttp
import asyncio
import requests

# run `python app.py` to start this server
BASE_URL = 'http://localhost:5000'
endpoints = ['', '/sleep', '/redirect', '/raises', '/chunked']
endpoints = ['']
URLS = [BASE_URL + endpoint for endpoint in endpoints]

# run `node websocket_server.js` to start the websockets server on port 8888
WS_URLS = ['http://example.com', 'http://localhost:8888']
WS_URLS = []

async def fetch(url):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            print('response.headers: ', response.headers)
            return await response.text()


async def ws_fetch(url):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.ws_connect(url) as ws:
            print('ws: ', ws)
            await ws.send_str('hello')
            async for msg in ws:
                print('msg: ', msg)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        await ws.send_str(msg.data + '/answer')
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break


async def fetch_multiple():
    coros = [fetch(url) for url in URLS]
    ws_coros = [ws_fetch(url) for url in WS_URLS]
    return await asyncio.gather(*coros, *ws_coros, return_exceptions=True)


def possibly_raise(text_list):
    for text in text_list:
        if isinstance(text, aiohttp.client_exceptions.ClientResponseError):
            raise text


#@print_nice_transaction_trace()
@newrelic.agent.background_task()
def main():
    loop = asyncio.get_event_loop()
    text_list = loop.run_until_complete(fetch_multiple())
    possibly_raise(text_list)


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
