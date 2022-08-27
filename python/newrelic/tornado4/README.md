# Tornado 4

## TCPServer

An exploration of tornado's TCPServer and how we could instrument it. This is
housed in the `tcp.py` and `socket_connect.js` files.

Start the tcp server with `python tcp.py`. Connect to it with the client using
Node.js. First do an `npm install net sleep` then you can run `node
socket_connect.js`. This will keep an open socket and send messages to the
server once every second.

It was discovered that the agent works fine if there is only one connection at
a time but once there are more, the transactions get all mixed up. Sadface.
