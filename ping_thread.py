import time

import requests
from dotenv import get_variable

from log_thread import LogThread
from sniffer_thread import SnifferThread

path_env = '/home/pi/smart-directions-anchor-init/.env'

FLASK_URL = get_variable(path_env, 'FLASK_URL')
PERIOD_CHECK = int(get_variable(path_env, 'PERIOD_CHECK'))

'''
With periodicity PERIOD_CHECK, a ping is sent to the server that confirms it is still alive.
If not, anchor waits for reconnection.
'''
class PingThread(LogThread):
    def __init__(self, name, mac):
        LogThread.__init__(self, name)
        self.mac = mac
        self.sniffer_thread = SnifferThread('Sniffer')

    def run(self):
        while True:
            try:
                r = requests.post("{}{}/ping".format(FLASK_URL, self.mac))
                code = r.status_code
                if code < 300:
                    if not self.sniffer_thread.is_alive():
                        self.sniffer_thread.start()
                else:
                    raise Exception("HTTP error")
            except:
                self.sniffer_thread.kill()
                self.sniffer_thread = SnifferThread('Sniffer')
            time.sleep(PERIOD_CHECK)

