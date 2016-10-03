#!/bin/bash

name=$1
name_title=`python -c "print '${name}'.replace('-', ' ').replace('_', ' ').title()"`
echo Starting app $name_title
shift

option=$1
case $option in
    --link)
        link=$2
        echo link:  $link
        echo Including link $link
        ;;
esac

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

if [[ $link != "" ]]
then
    echo >> README.md
    echo $link >> README.md
fi
