import subprocess
import threading
from os.path import join

from dotenv import get_variable

from log_thread import LogThread

import os


class LedThread(LogThread):
    def __init__(self, name, color, direction, execution_time, connection):
        LogThread.__init__(self, name)
        self.process = None
        self.connection = connection    # socket towards c++
        self.direction, self.color, self.execution_time = direction, color, execution_time

    def run(self):
        msg = str.encode("{}${}${}".format(self.direction, self.color, self.execution_time))
        if self.connection is not None:
            self.log("SEND MSG: {}".format(msg))
            self.connection.sendall(msg)

    def kill(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None