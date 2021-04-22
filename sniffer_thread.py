import subprocess
import threading
from os.path import join

from dotenv import get_variable

from log_thread import LogThread


path_env = '/home/pi/smart-directions-anchor-init/.env'

class SnifferThread(LogThread):
    def __init__(self, name):
        LogThread.__init__(self, name)
        self.process = None

    def run(self):
        base_path_scanner = get_variable(path_env, 'BASE_PATH_SCANNER')
        command = join(base_path_scanner, "cmake-build-rasp1/ble_scanner")
        # running c++ code for sniffing
        self.process = subprocess.Popen([command])
        self.process.wait()

    def kill(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None