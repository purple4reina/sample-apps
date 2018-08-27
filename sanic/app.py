from sanic import Sanic
from sanic.response import json

app = Sanic()

@app.route('/')
async def index(request):
    return json({'hello': 'world'})

if __name__ == '__main__':
    app.run()
