from websocket import create_connection
from flask import Flask, request, make_response, jsonify
import json, time, logging
from uuid import uuid4

get_millis=lambda:int(round(time.time()*1000))
api_key = str(uuid4())
logging.basicConfig(level=logging.DEBUG)
device_ip = "192.168.0.24"
device_id = "100054e0f8"
server_port = 8080
websocket = None

app = Flask(__name__)

def on_open(ws):
    payload = {
        "action":    "userOnline",
        "ts":        str(int(get_millis() / 1000)),
        "version":   6,
        "apikey":    api_key,
        "sequence":  str(get_millis()),
        "userAgent": "app"
    }
    ws.send(json.dumps(payload))

def generate_switch_payload(dev_id, state1=False, state2=False):
    switch1_state = "on" if state1 else "off"
    switch2_state = "on" if state2 else "off"
    payload = {
        "action": "update",
        "deviceid": dev_id,
        "apikey": api_key,
        "userAgent": "app",
        "sequence": str(int(time.time() * 1000)),
        "params": {
            "switches": [
                {
                    "switch": switch1_state,
                    "outlet": 0
                },
                {
                    "switch": switch2_state,
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
        }
    }
    return payload


@app.route('/')
def main_route():
    return make_response('OK', 200)

# Use this route to alter switch state
@app.route('/state', methods=['POST'])
def state_switches():
    global websocket, device_id
    if websocket == None:
        return make_response("Websockets connection not established. Unable to control switch")
    else:
        command = request.json
        payload = generate_switch_payload(device_id, command['0'], command['1'])
        websocket.send(json.dumps(payload))
    return make_response('STATE', 200)

if __name__ == '__main__':
    logging.info("Establishing WS connection to Sonoff at {}:{}".format(device_ip, 8081))
    websocket = create_connection("ws://192.168.0.24:8081", subprotocols=['chat'])
    on_open(websocket)
    logging.info("Starting HTTP server on port {}".format(server_port))
    app.run(host='192.168.0.22', port=8080, debug=True)