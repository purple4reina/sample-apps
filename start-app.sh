#!/bin/bash

name=$1
name_title=`python -c "print '${name}'.replace('-', ' ').replace('_', ' ').title()"`

mkdir $name
cd $name

cp ../newrelic.ini newrelic.ini
sed -i '' "s/app_name = .*/app_name = ${name_title}/g" newrelic.ini

virtualenv env
source env/bin/activate
cp ../requirements.txt .
pip install -r requirements.txt

cat > app.py <<EOF
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(debug=True)
EOF

cat > README.md <<EOF
# ${name_title}
EOF
