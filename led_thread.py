import subprocess
import threading
from os.path import join

from dotenv import get_variable

from log_thread import LogThread

import os

path_env = '/home/pi/smart-directions-slave/.env'

abs_path_arrow = "{}/../assets/".format(os.path.dirname(os.path.realpath(__file__)))
print("PATH: {}".format(abs_path_arrow))
PATH_ASSETS = get_variable(path_env, 'PATH_ASSETS')

class LedThread(LogThread):
    def __init__(self, name, color, direction, execution_time, connection):
        LogThread.__init__(self, name)
        self.process = None
        self.connection = connection    # socket towards c++
        self.direction, self.color, self.execution_time = direction, color, execution_time

    def run(self):
        msg = str.encode("{}${}${}".format(self.direction, self.color, self.execution_time))
        if self.connection is not None:
            self.connection.sendall(msg)

    def kill(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None