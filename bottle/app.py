import bottle
import customer_files

app = bottle.Bottle()

@customer_files.get('/', app)
def orangehat():
    return '*'

if __name__ == '__main__':
    bottle.run(
            app=app,
            host='localhost',
            port=8000,
            reloader=True,
            debug=True,
    )
