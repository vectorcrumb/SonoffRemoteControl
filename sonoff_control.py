import json, requests, warnings
from urllib3.connectionpool import InsecureRequestWarning

class SonoffController():

    def __init__(self, ip_server, port_server):
        self.switch0 = False
        self.switch1 = False
        self.server_ip = ip_server
        self.server_port = str(port_server)
    
    def set_state(self, switch0_state=False, switch1_state=False):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            req_state = requests.post("https://" + self.server_ip + ":" + self.server_port + "/state", json=
            {
                "0": switch0_state,
                "1": switch1_state
            }, headers={
                "Content-Type": "application/json"
            }, verify=False)