import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import aiohttp
import asyncio

URLS = ['https://example.com', 'https://example.org']


async def fetch(url, client):
    async with client.get(url) as resp:
        return await resp.text()


async def multi_fetch():
    async with aiohttp.ClientSession(raise_for_status=True) as client:
        text_coros = [fetch(u, client) for u in URLS]
        return await asyncio.gather(*text_coros)


@newrelic.agent.background_task()
def main():
    loop = asyncio.get_event_loop()
    text_list = loop.run_until_complete(multi_fetch())
    print('text_list: ', text_list)


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
