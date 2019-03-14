const WebSocket = require('ws');
const express = require('express');
const bodyParser = require('body-parser');
var fs = require('fs');

var configFile = fs.readFileSync("../config_lan.json");
var configs = JSON.parse(configFile);
const IPADDRESS = configs['device']['IPwifi'];
const PORT = 8080;
console.log("Starting up SonoffControl server on port %d ...", PORT);
console.log("WS Client connecting to %s:%d", IPADDRESS, 8081);

const seq = () => String(Date.now());
const ws = new WebSocket('ws://' + IPADDRESS + ':8081', [ 'chat' ]);
const nonce = 'nonce';
let connected = false;

var app = express();
app.use(bodyParser.json());
app.listen(8080);

console.log("Server started. WS connected");

// Accept state changes via a POST request
app.post('/state', function(req, res) {
    console.log("Received following state change payload: %s", req.body);
    if ((req.body['0'] != 'on' && req.body['0'] != 'off') || (req.body['1'] != 'on' && req.body['1'] != 'off')) {
        res.status(500).send('Faulty packet');
    } else if (!connected) {
        res.status(500).send('Sonoff not connected');
    } else {
        updateState(req.body['0'], req.body['1']);
        res.status(200).send('state');
    }
});

// Log all messages received from the device
ws.on('message', function incoming(json) {
  const messageData = JSON.parse(json);
  console.log('Received Message: %j', messageData);
});

// Define method to send update message to change switch state
function updateState(newState1, newState2) {
  const updateMessageJSON = JSON.stringify({
    "action": "update",
    "deviceid": nonce,
    "apikey": nonce,
    "selfApikey": nonce,
    "params": {
        "switches": [
            {
                "switch": newState1,
                "outlet": 0
            },
            {
                "switch": newState2,
                "outlet": 1
            },
            {
                "switch": "off",
                "outlet": 2
            },
            {
                "switch": "off",
                "outlet": 3
            }
        ]
    },
    "sequence": seq(),
    "userAgent": "app"
  });
  console.log('Sending Update Message: %s', updateMessageJSON);
  ws.send(updateMessageJSON);
}

// Initiate session with device in LAN mode by sending "userOnline" action message
ws.on('open', function initiateSession(ev) {
  const initiateSessionMessageJSON = JSON.stringify({
    "action":    "userOnline",
    "ts":        String(0 | Date.now / 1000),
    "version":   6,
    "apikey":    nonce,
    "sequence":  seq(),
    "userAgent": "app"
  });
  connected = true;
  console.log('Sending User Online Message: %s', initiateSessionMessageJSON);
  ws.send(initiateSessionMessageJSON);
});