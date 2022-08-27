# Investigation of [this ticket](https://newrelic.zendesk.com/agent/tickets/196417)


## Set up the MySQL database
1. start mysql database in a docker container `docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password --name mysql mysql`
1. log into it `docker exec -it mysql bash`
1. get into the mysql shell `mysql -u root`
1. create a new user with all privileges `CREATE USER 'reina'@'%' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON *.* TO 'reina'@'%' WITH GRANT OPTION;`
1. create the database `CREATE DATABASE db CHARACTER SET utf8;`
1. you can save this container to a tar file with `docker export mysql > mysql-container.tar`


## Set up the Toxiproxy container
+ start the container with `docker run -d --name toxiproxy -p 8474:8474 -p 33306:33306 shopify/toxiproxy`
  - 8474 is the toxiproxy api port
  - 33306 will be the port to proxy to mysql
  - start the proxy with `python toxiproxy_controller.py`
+ to enable/disable the toxicity:
  - stop with `./toxiproxy_controller.py stop`
  - change the latency with `./toxiproxy_controller.py start <value>` where <value> is the latency value in milliseconds (I think?)
  - start the latency with default values with `./toxiproxy_controller.py`


## Running with gunicorn
+ to start the app with gunicorn and the agent `NEW_RELIC_CONFIG_FILE=../newrelic.ini newrelic-admin run-program gunicorn testingapp.wsgi:application --log-file - --log-level DEBUG --timeout 1 --config testingapp/gunicorn_config.py`
+ all logging is to stdout/stderr including django logs (which is configured in settings.py to go to console)


## Recreate `OperationalError: (2006, 'MySQL server has gone away')` error
To recreate the traceback with `OperationalError: (2006, 'MySQL server has gone away')`, start the gunicorn server then do a get request to http://localhost:8000/dumbo/go_away/. You can do this with curl or your browser.

The `go_away` view uses toxiproxy to simulate the situation where the connection between the mysql server and the django web server has been cut. It cuts the connection, then makes a call to create a new object in the database. Before raising the error, it re-enables the mysql network connection.
