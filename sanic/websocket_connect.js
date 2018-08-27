var WebSocket = require('ws');

path = process.argv[2];

ws = new WebSocket(path);
console.log("New WebSocket created:\n", ws, "\n");

ws.onmessage = function(e) {
    console.log("Message received: ", e.data);
    console.log("Sending message back...");
    ws.send("Hello back!");
}
