# Investigation of [this ticket](https://newrelic.zendesk.com/agent/tickets/196417)


## Set up the MySQL database
1. start mysql database in a docker container `docker run -d -p 3306:3306 -e
MYSQL_ROOT_PASSWORD=password --name mysql mysql`
1. log into it `docker exec -it mysql bash`
1. get into the mysql shell `mysql -u root`
1. create a new user with all privileges `CREATE USER 'reina'@'%' IDENTIFIED BY
'password'; GRANT ALL PRIVILEGES ON *.* TO 'reina'@'%' WITH GRANT OPTION;`
1. create the database `CREATE DATABASE db CHARACTER SET utf8;`
