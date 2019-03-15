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
X_INPUT_CODE = 'ABS_RX'
Y_INPUT_CODE = 'ABS_RY'
X_CHANNEL = 1
Y_CHANNEL = 2

# UDP client settings
CLIENT_MIN_DELAY = 0.01
SERVER_IP = '192.168.88.249'
SERVER_PORT = 5005


def position_to_percents(value):
    if LEFT_THRESHOLD < value < RIGHT_THRESHOLD:
        return 0
    if value < 0:
        return - value * 100 / LEFT_MAX
    return value * 100 / RIGHT_MAX


class MzClient:
    current_x_value = 0
    driver_x_value = 0
    current_y_value = 0
    driver_y_value = 0
    sock = None

    def events_handling_loop(self):
        while 1:
            events = get_gamepad()
            for event in events:
                if event.code == X_INPUT_CODE:
                    self.current_x_value = position_to_percents(event.state)
                elif event.code == Y_INPUT_CODE:
                    self.current_y_value = position_to_percents(event.state)

    def rest_client_loop(self):
        while 1:
            time.sleep(CLIENT_MIN_DELAY)
            if self.driver_x_value != self.current_x_value:
                self.driver_x_value = self.current_x_value
                self.sock.sendto(struct.pack('bfq', X_CHANNEL, self.driver_x_value, current_millis()),
                                 (SERVER_IP, SERVER_PORT))
                print("X set to {}".format(self.driver_x_value))
            elif self.driver_y_value != self.current_y_value:
                self.driver_y_value = self.current_y_value
                self.sock.sendto(struct.pack('bfq', Y_CHANNEL, self.driver_y_value, current_millis()),
                                 (SERVER_IP, SERVER_PORT))
                print("Y set to {}".format(self.driver_y_value))

    def startup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Thread(target=self.events_handling_loop).start()
        Thread(target=self.rest_client_loop()).start()


client = MzClient()
client.startup()
