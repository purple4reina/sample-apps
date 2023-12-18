var net = require('net');
var sleep = require('sleep');

var client = new net.Socket();

client.connect(8888, 'localhost', function() {
    console.log('Connected');

    while (true) {
        console.log("sending data");
        client.write("Hello World!\n");
        sleep.sleep(1);
    }
});

client.on('data', function(data) {
    console.log('Received: ' + data);
});

client.on('close', function() {
    console.log('Connection closed');
});
