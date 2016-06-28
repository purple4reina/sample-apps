var WebSocket = require('ws');

ws = WebSocket("ws://localhost:5000");
console.log("New WebSocket created:\n", ws, "\n");

ws.onmessage = function(e) {
    console.log("Message received: ", e.data);
    console.log("Sending message back...");
    ws.send("Hello back!");
}
