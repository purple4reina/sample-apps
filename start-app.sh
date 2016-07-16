#!/bin/bash

name=$1

mkdir $name
cd $name

cp ../newrelic.ini .
cp ../requirements.txt .

virtualenv env
source env/bin/activate
pip install -r requirements.txt

cat > app.py <<EOL
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
EOL
