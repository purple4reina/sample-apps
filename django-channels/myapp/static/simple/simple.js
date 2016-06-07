$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var simplesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);
    var conDiv = $('#connections');
    var msgDiv = $('#messages');

    simplesock.onmessage = function(e) {
        var data = JSON.parse(e.data);

        // update number of connections
        conDiv.text(data.connections);

        // if there is a new message, add it!
        msgDiv.append('<p>' + data.message + '</p>');
    }

    $('form').on('submit', function(e) {
        e.preventDefault();

        var text = $('#sendmessage').val();
        simplesock.send(text);

        // clear the text box
        $('#sendmessage').val('');
    });

});
