from flask import Flask

ecs_id_mapper = Flask(__name__)

@ecs_id_mapper.route('/')
def NO():
    return 'Hello world\n'
