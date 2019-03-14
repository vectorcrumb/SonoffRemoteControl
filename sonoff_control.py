import json, requests

class SonoffController():

    def __init__(self, ip_server, port_server):
        self.switch0 = False
        self.switch1 = False
        self.server_ip = ip_server
        self.server_port = str(port_server)
    
    def set_state(self, switch0_state=False, switch1_state=False):
        req_state = requests.post("http://" + self.server_ip + ":" + self.server_port + "/state", json=
        {
            "0": 'on' if switch0_state else 'off',
            "1": 'on' if switch1_state else 'off'
        }, headers={
            "Content-Type": "application/json"
        })
        return req_state.status_code