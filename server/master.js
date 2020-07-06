const dgram = require('dgram');
const udpServer = dgram.createSocket('udp4');
const udpClient = dgram.createSocket('udp4');

//const config = require('config');
//const params = config.get('default');

const app = require('express')();
const httpServer = require('http').Server(app);
const io = require('socket.io')(httpServer, { path: '/feed/monitor' });

udpServer.on('error', (err) => {
  console.log(`server error:\n${err.stack}`);
  udpServer.close();
});

udpServer.on('message', (msg, rinfo) => {
  node_data = JSON.parse(msg.toString());
  io.compress(true)
    .to(node_data['node']['id'] + '_room')
    .emit('broadcast', JSON.stringify(node_data))
});

udpServer.on('listening', () => {
  const address = udpServer.address();
  console.log(`server listening ${address.address}:${address.port}`);
});

udpServer.bind(20002);

io.on('connection', socket => {
  console.log(`${socket.id} connected`);
  socket.emit('broadcast', 'Welcome to Dashboard Monitor (Build: 20200618)');

  //Get more than one machine details
  socket.on('pageload', input => {
    if (typeof input['node'] !== 'undefined') {
      nodes = (input['node']).split(",");
      nodes.forEach(node => {
        socket.join(node + '_room');
        console.log(`${socket.id} joined room ${node}`);
      });
    }
  });
  //Remove user from all rooms
  socket.on('pageunload', input => {
    socket.leaveAll();
    console.log(`${socket.id} left all rooms`);
  });
  //Get server details
  socket.on('serverload', input => {
    if (typeof input['node'] !== 'undefined') {
      socket.join(input['node'] + '_room');
      console.log(`${socket.id} joined room ${input['node']}`);
    }
  });
  //Remove user from specific room
  socket.on('serverunload', input => {
    if (typeof input['node'] !== 'undefined') {
      nodes = (input['node']).split(",");
      nodes.forEach(node => {
        socket.leave(node + '_room');
        console.log(`${socket.id} left room ${node}`);
      });
    }
  });

  socket.on('process', input => {
    if (typeof input['action'] !== 'undefined') {
      console.log(input['action']);
      if (typeof input['node'] !== 'undefined') {
        nodes = (input['node']).split(",");
        nodes.forEach(ip => {
          udpClient.send(input['action'], 0, (input['action']).length, 8082, ip, function (err) {
            if (err) {
              console.log(err);
            }
          });
        });
      }
    }
  });

});
httpServer.listen(8080, () => {
  console.log(`Server listening on ${httpServer.address().address}:${httpServer.address().port}`);
});