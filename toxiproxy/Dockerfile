FROM shopify/toxiproxy:2.1.3

EXPOSE 22220-22222

ADD toxiproxy.json /root/toxiproxy.json

CMD ["-host=0.0.0.0", "-config=/root/toxiproxy.json"]
