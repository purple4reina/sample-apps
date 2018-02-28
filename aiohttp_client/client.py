import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import aiohttp
import asyncio

URLS = ['http://0.0.0.0:5000']


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=0.1) as response:
            print('url: ', url)
            print('response.headers: ', response.headers)
            return await response.text()


async def fetch_multiple():
    coros = [fetch(url) for url in URLS]
    return await asyncio.gather(*coros)


@newrelic.agent.background_task()
def main():
    loop = asyncio.get_event_loop()
    text_list = loop.run_until_complete(fetch_multiple())


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
