env/bin/newrelic-admin run-program env/bin/uwsgi --single-interpreter --enable-threads --http :8000 --wsgi wsgi:application --virtualenv env --py-autoreload 1
