import requests, json


with open('config_lan.json') as config_f:
    configs = json.load(config_f)

wifi_ssid = configs['network']['SSID']
wifi_password = configs['network']['password']
wifi_server_name = configs['server']['IP']
wifi_server_port = configs['server']['port']
sonoff_protocol = configs['device']['protocol']
sonoff_ip = configs['device']['IP']

# Begin by connecting to device via a GET request @ 10.10.7.1/device
req_get_device_id = requests.get(sonoff_protocol + sonoff_ip + "/device")
print("REQA | {}".format(req_get_device_id.text))
configs['device']['deviceid'] = str(req_get_device_id.json()['deviceid'])
configs['device']['apikey'] = str(req_get_device_id.json()['apikey'])
print("Update device ID and API key. Storing the following config file: {}".format(configs))
with open('config.json', 'w') as config_f:
    json.dump(configs, config_f, indent=4, sort_keys=True)

# Send a post with SSID information to connect Sonoff device
req_set_device_wifi = requests.post(sonoff_protocol + sonoff_ip + "/ap", json={
    "version": 4,
    "ssid": wifi_ssid,
    "password": wifi_password,
    "serverName": wifi_server_name,
    "port": wifi_server_port
}, headers={
    "Content-Type": "application/json"
})
print("REQA | {}".format(req_set_device_wifi.text))
