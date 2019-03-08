from flask import Flask, request, make_response, jsonify
from flask_sockets import Sockets
from geventwebsocket.exceptions import WebSocketError
import gevent
import json, requests, time
from datetime import datetime
from uuid import uuid4

app = Flask(__name__)
sockets = Sockets(app)

state = False
ws_ref = None
device_id = None

with open('config.json') as config_f:
    configs = json.load(config_f)

wifi_ssid = configs['network']['SSID']
wifi_password = configs['network']['password']
wifi_server_name = configs['server']['IP']
wifi_server_port = configs['server']['port']
wifi_wsserver_port = configs['server']['wsport']
uuidkey = str(uuid4())

def generate_switch_payload(dev_id, state1=False, state2=False):
    switch1_state = "on" if state1 else "off"
    switch2_state = "on" if state2 else "off"
    payload = {
        "action": "update",
        "deviceid": dev_id,
        "apikey": uuidkey,
        "userAgent": "app",
        "sequence": str(int(time.time() * 1000)),
        "ts": 0,
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
        },
        "from": "app"
    }
    return payload

def tick_tock(delay):
    print("POST Heartbeat: Tic")
    time.sleep(delay)
    print("POST Heartbeat: Toc")

@app.route('/')
def main_route():
    return make_response('OK')

@app.route('/on')
def on_switches():
    global device_id, ws_ref
    if ws_ref == None or device_id == None:
        return make_response("Websockets connection not established. Unable to control switch")
    else:
        payload = generate_switch_payload(device_id, True, True)
        ws_ref.send(json.dumps(payload))
    return make_response("on")


@app.route('/off')
def off_switches():
    global device_id, ws_ref
    if ws_ref == None or device_id == None:
        return make_response("Websockets connection not established. Unable to control switch")
    else:
        payload = generate_switch_payload(device_id)
        ws_ref.send(json.dumps(payload))
    return make_response("off")


@app.route('/dispatch/device', methods=['POST'])
def ws_config():
    global state
    print("REQ | {} | {}".format(request.method, request.url))
    print("REQ | {}".format(request.json))
    if (request.json['deviceid'] == '100024ff33'):
        state = True
    gevent.spawn(tick_tock, 0.5)
    payload = {
        "error": 0,
        "reason": "ok",
        "IP": wifi_server_name,
        "port": wifi_wsserver_port
    }
    resp = make_response(json.dumps(payload))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@sockets.route('/api/ws')
def print_socket(websocket):
    global ws_ref, device_id
    ws_ref = websocket
    print("WS | Initiated")
    while not websocket.closed:
        message = websocket.receive()
        print("WS | INCOMING: {}".format(message))
        if message != None:
            mjson = json.loads(message)
            if 'deviceid' in mjson:
                device_id = mjson['deviceid']
            if 'action' in mjson:
                print("WS | Action {} requested".format(mjson['action']))
                if mjson['action'] == "register":
                    if "model" in mjson and mjson["model"]:
                        device_model = mjson["model"]
                        print("We are dealing with a {} model.".format(device_model))
                    payload = {
                        "error": 0,
                        "deviceid": mjson['deviceid'],
                        "apikey": uuidkey,
                        "config": {
                            "hb": 1,
                            "hbInterval": 145
                        }
                    }
                    print("WS | register | Sending: {}".format(payload))
                    websocket.send(json.dumps(payload))
                if mjson['action'] == 'date':
                    payload = {
                        "error": 0,
                        "deviceid": mjson['deviceid'],
                        "apikey": uuidkey,
                        "date": datetime.isoformat(datetime.today())[:-3] + 'Z'
                    }
                    print("WSR | date | Sending: {}".format(payload))
                    websocket.send(json.dumps(payload))
                if mjson['action'] == "query":
                    payload = {
                        "error": 0,
                        "deviceid": mjson['deviceid'],
                        "apikey": uuidkey,
                        "params": 0
                    }
                    print("WS | query | Sending: {}".format(payload))
                    websocket.send(json.dumps(payload))
                if mjson['action'] == "update":
                    payload = {
                        "error": 0,
                        "deviceid": mjson['deviceid'],
                        "apikey": uuidkey
                    }
                    print("WS | update | Sending: {}".format(payload))
                    websocket.send(json.dumps(payload))
            else:
                print("WSR | unknown | {}".format(message))
    if websocket.closed:
        print("WS | Closed")


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler as WSH

    app.config['SECRET_KEY'] = 'zippedi'

    print("HTTPS | Starting web server on {}:{}".format(wifi_server_name, wifi_server_port))

    server = pywsgi.WSGIServer(('0.0.0.0', wifi_server_port), app, handler_class=WSH, keyfile=configs['ssl']['key'], certfile=configs['ssl']['cert'])
    server.serve_forever()
