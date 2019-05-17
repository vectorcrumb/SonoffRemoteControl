import json, requests
import time

class SonoffController():

    def __init__(self, ip_server, port_server):
        self.switch0 = False
        self.switch1 = False
        self.server_ip = ip_server
        self.server_port = str(port_server)
    
    def set_state(self, switch0_state=False, switch1_state=False):
        """Sets sonoff dual state via an POST request to the node server
        
        Keyword Arguments:
            switch0_state {bool} -- State of switch 0 (default: {False})
            switch1_state {bool} -- State of switch 1 (default: {False})
        
        Returns:
            status_code -- Status code of HTTP request. A code 500 indicates an error.
        """

        req_state = requests.post("http://" + self.server_ip + ":" + self.server_port + "/state", json=
        {
            "0": 'on' if switch0_state else 'off',
            "1": 'on' if switch1_state else 'off'
        }, headers={
            "Content-Type": "application/json"
        })
        return req_state.status_code

    def open(self, timer=30):
        self.set_state(True, False)
        t = time.time()
        while(time.time()<t+timer):
            pass
        self.set_state(False, False)

    def close(self, timer=30):
        self.set_state(False, True)
        t = time.time()
        while(time.time()<t+timer):
            pass
        self.set_state(False, False)

