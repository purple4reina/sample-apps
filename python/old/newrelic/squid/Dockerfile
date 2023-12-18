FROM ubuntu:16.04

EXPOSE 3128

RUN apt-get update && \
    apt-get install -y squid

ADD squid.conf /root/squid.conf

# -N    no daemon
# -X    full debug mode
# -d2   higher logging level
# -f    specify config file other than /etc/squid/squid.conf
CMD ["/usr/sbin/squid", "-N", "-X", "-d2", "-f", "/root/squid.conf"]
