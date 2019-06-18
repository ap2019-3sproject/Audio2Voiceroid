const PORT = process.env.PORT || 3939;
var net = require('net');

var clients = [];

var server = net.createServer(function(conn){
  console.log('server-> tcp server created');
  conn.name = conn.remoteAddress + ":" + conn.remotePort;
  clients.push(conn);

  conn.on('data', function(data){
    console.log('server-> ' + data + ' from ' + conn.remoteAddress + ':' + conn.remotePort);
    broadcast(data, conn);
  });
  conn.on('close', function(){
    console.log('server-> client closed connection');
	var i = 0;
    clients.forEach(function (client) {
      if (client === conn) clients.splice(i, 1);
	  i += 1;
    });
	
  });

  function broadcast(message, sender) {
    clients.forEach(function (client) {
      // Don't want to send it to sender
      if (client === sender) return;
      client.write(message);
    });
    // Log it to the server output too
    console.log(message);
  }
}).listen(PORT);

console.log('listening on port ' + PORT);

