from sonoff_control import SonoffController
from time import sleep

sonoff = SonoffController('localhost', '8080')

sonoff.set_state(False, False)
sleep(0.5)
print(sonoff.set_state(True, False))
sleep(2)
sonoff.set_state(False, False)
sleep(2)
sonoff.set_state(False, True)
sleep(2)
sonoff.set_state(False, False)
