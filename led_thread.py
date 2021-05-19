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
EXECUTION_TIME = get_variable(path_env, 'EXECUTION_TIME')

class LedThread(LogThread):
    def __init__(self, name, relative_message_to_show):
        LogThread.__init__(self, name)
        self.process = None

        suffix = {
            '1': 'top',
            '2': 'right',
            '3': 'bottom',
            '4': 'left',
            '5': 'all'
        }

        arrow_to_show = suffix[relative_message_to_show]
        self.filename = 'arrow-{}.gif'.format(arrow_to_show)

    def run(self):
        # sudo ./led-image-viewer ../bindings/python/own_samples/arrow.gif  --led-gpio-mapping=adafruit-hat
        base_led_image_path = get_variable(path_env, 'BASE_PATH_SCANNER')
        #command = join(base_led_image_path, "led-image-viewer {}{}".format(abs_path_arrow, self.filename))
        command = ['timeout', '{}s'.format(EXECUTION_TIME), join(base_led_image_path, 'led-image-viewer'), '--led-gpio-mapping=adafruit-hat', "{}/{}".format(PATH_ASSETS, self.filename)]#join(base_led_image_path, "led-image-viewer --led-gpio-mapping=adafruit-hat {}/{}".format(PATH_ASSETS, self.filename))
        # running c++ code for sniffing
        print("DBG: {}".format(command))
        self.process = subprocess.Popen(command)
        self.process.wait()

    def kill(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None