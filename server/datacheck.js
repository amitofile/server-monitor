const dgram = require('dgram');
const udpServer = dgram.createSocket('udp4');

const app = require('express')();
const httpServer = require('http').Server(app);
const io = require('socket.io')(httpServer, { path: '/feed/monitor' });

udpServer.on('error', (err) => {
  console.log(`server error:\n${err.stack}`);
  udpServer.close();
});

udpServer.on('message', (msg, rinfo) => {
  //console.log(`server got: ${msg} from ${rinfo.address}:${rinfo.port}`);
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
  socket.emit('broadcast', 'Welcome to Dashboard Monitor (Build: 20200609)');

  socket.on('pageload', input => {
    if (typeof input['node'] !== 'undefined') {
      socket.join(input['node'] + '_room');
      console.log(`${socket.id} joined room ${input['node']}`);
    }
  });
});
httpServer.listen(8080, () => {
  console.log(`Server listening on ${httpServer.address().address}:${httpServer.address().port}`);
});