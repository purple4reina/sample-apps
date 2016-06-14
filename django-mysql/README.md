# Investigation of [this ticket](https://newrelic.zendesk.com/agent/tickets/196417)


## Set up the MySQL database
1. start mysql database in a docker container `docker run -d -p 3306:3306 -e
MYSQL_ROOT_PASSWORD=password --name mysql mysql`
1. log into it `docker exec -it mysql bash`
1. get into the mysql shell `mysql -u root`
1. create a new user with all privileges `CREATE USER 'reina'@'%' IDENTIFIED BY
'password'; GRANT ALL PRIVILEGES ON *.* TO 'reina'@'%' WITH GRANT OPTION;`
1. create the database `CREATE DATABASE db CHARACTER SET utf8;`


## Set up the Toxiproxy container
+ start the container with `docker run -d --name toxiproxy -p 8474:8474 -p 33306:33306 shopify/toxiproxy`
  - 8474 is the toxiproxy api port
  -  33306 will be the port to proxy to mysql
+ to enable/disable the toxicity:
  - stop with `./toxiproxy_controller.py stop`
  - change the latency with `./toxiproxy_controller.py start <value>` where <value> is the latency value in milliseconds (I think?)
  - start the latency with default values with `./toxiproxy_controller.py`
