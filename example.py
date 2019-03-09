from sonoff_control import SonoffController
from time import sleep

sonoff = SonoffController('192.168.0.22', '1081')

sonoff.set_state(False, False)
sleep(0.5)
sonoff.set_state(True, False)
sleep(2)
sonoff.set_state(False, False)
sleep(2)
sonoff.set_state(False, True)
sleep(2)
sonoff.set_state(False, False)
