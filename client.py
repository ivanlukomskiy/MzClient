import json
import time
from threading import Thread

import urllib3
from inputs import get_gamepad

# Controller settings
LEFT_THRESHOLD = -3000
RIGHT_THRESHOLD = 3000
LEFT_MAX = -32768
RIGHT_MAX = 32767
INPUT_CODE = 'ABS_RX'

# Rest client settings
REST_CLIENT_MIN_DELAY = 0.2
API_URI = 'http://localhost:8000'
HEADERS = {'Connection': 'close'}
PATH = "{}/api/servo/y/velocity".format(API_URI)

http = urllib3.PoolManager()


def position_to_percents(value):
    if LEFT_THRESHOLD < value < RIGHT_THRESHOLD:
        return 0
    if value < 0:
        return - value * 100 / LEFT_MAX
    return value * 100 / RIGHT_MAX


class MzClient:
    currentValue = 0
    driverValue = 0

    def events_handling_loop(self):
        while 1:
            events = get_gamepad()
            for event in events:
                if event.code != INPUT_CODE:
                    continue
                self.currentValue = position_to_percents(event.state)

    def rest_client_loop(self):
        while 1:
            time.sleep(0.2)
            if self.driverValue == self.currentValue:
                continue
            self.driverValue = self.currentValue
            encoded_data = json.dumps({"value": self.driverValue}).encode('utf-8')
            start = time.time()
            r = http.request('PUT', PATH, body=encoded_data)
            val = json.loads(r.data.decode('utf-8'))['value']
            end = time.time()
            print("Velocity updated: {0:.2f}, took {1:.4f} sec".format(val, (end - start)))

    def startup(self):
        Thread(target=self.events_handling_loop).start()
        Thread(target=self.rest_client_loop()).start()


client = MzClient()
client.startup()
