# This isn't working right, so don't use it

FROM mysql

EXPOSE 3306

ENV MYSQL_ROOT_PASSWORD=password

CMD mysqld_safe & \
    mysql -u root -e \
        "CREATE USER 'reina'@'%' \
            IDENTIFIED BY 'password'; \
        GRANT ALL PRIVILEGES ON *.* TO 'reina'@'%' \
            WITH GRANT OPTION; \
        CREATE DATABASE db CHARACTER SET utf9;" ; \
    tail -f /var/log/mysql.err /var/log/mysql.log
