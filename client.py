import json
import socket
import struct
import time
from threading import Thread
current_millis = lambda: int(round(time.time() * 1000))

from inputs import get_gamepad

# Controller settings
LEFT_THRESHOLD = -3000
RIGHT_THRESHOLD = 3000
LEFT_MAX = -32768
RIGHT_MAX = 32767
INPUT_CODE = 'ABS_RX'

# UDP client settings
CLIENT_MIN_DELAY = 0.01
SERVER_IP = '192.168.88.249'
SERVER_PORT = 5005
LOWERING_COEFFICIENT = 0.3
SHIFT = -1.5


def position_to_percents(value):
    if LEFT_THRESHOLD < value < RIGHT_THRESHOLD:
        return SHIFT
    if value < 0:
        return - value * 100 * LOWERING_COEFFICIENT / LEFT_MAX + SHIFT
    return value * 100 * LOWERING_COEFFICIENT / RIGHT_MAX + SHIFT


class MzClient:
    currentValue = 0
    driverValue = 0
    sock = None

    def events_handling_loop(self):
        while 1:
            events = get_gamepad()
            for event in events:
                if event.code != INPUT_CODE:
                    continue
                self.currentValue = position_to_percents(event.state)

    def rest_client_loop(self):
        while 1:
            time.sleep(CLIENT_MIN_DELAY)
            if self.driverValue == self.currentValue:
                continue

            self.driverValue = self.currentValue
            self.sock.sendto(struct.pack('bf', 1, self.driverValue, current_millis()),
                             (SERVER_IP, SERVER_PORT))
            print("Set to {}".format(self.driverValue))


    def startup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Thread(target=self.events_handling_loop).start()
        Thread(target=self.rest_client_loop()).start()



client = MzClient()
client.startup()
