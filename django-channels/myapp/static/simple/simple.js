$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var simplesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);
});
