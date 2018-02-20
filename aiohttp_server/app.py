from aiohttp import web
import asyncio


async def doit(num):
    await asyncio.sleep(0)
    return num


async def handle(request):
    coros = [doit(i) for i in range(10)]
    await asyncio.gather(*coros)
    return web.Response(text='*')


app = web.Application()
app.router.add_get('/', handle)


if __name__ == '__main__':
    web.run_app(app)
