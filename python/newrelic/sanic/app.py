import aiohttp

from sanic import Sanic
from sanic.response import json, stream

app = Sanic()


@app.route('/')
async def index(request):
    async def streaming_fn(response):
        await response.write('foo')
        await response.write('bar')
    return stream(streaming_fn)


@app.route('/cat')
async def cat(request):
    async with aiohttp.ClientSession(raise_for_status=True) as client:
        async with client.get('http://localhost:8000/') as resp:
            return json(dict((key, value) for key, value in resp.headers.items()))


if __name__ == '__main__':
    app.run(debug=True)
