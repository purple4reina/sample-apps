from sanic import Sanic
from sanic.response import json

app = Sanic()


@app.route('/')
async def index(request):
    return json({'hello': 'world'})


@app.middleware('request')
async def request_middleware(request):
    return json({'oops': 'wrong'})


@app.websocket('/ws')
async def feed(request, ws):
    data = 'hello!'
    print('Sending: ' + data)
    await ws.send(data)
    data = await ws.recv()
    print('Received: ' + data)


if __name__ == '__main__':
    app.run()
