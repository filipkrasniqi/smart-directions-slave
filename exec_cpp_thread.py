from log_thread import LogThread
import subprocess

class ExecCPPThread(LogThread):

    def __init__(self):
        LogThread.__init__(self, "Exec CPP")
        self.is_initialized = False
        self.active = True

    def update_status(self, msg):
        if "created" in msg:
            self.is_initialized = True
        # TODO handle if has any error. Should close all thread.
        
    def execute(self, command):
        self.popen = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(self.popen.stdout.readline, ""):
            self.update_status(stdout_line)
            yield stdout_line 
        self.popen.stdout.close()
        return_code = self.popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)

    def run(self):
        # Example
        while self.active:
            for path in self.execute(["/home/pi/smart-directions-slave-led/utils/led-image-loader"]):
                if not self.active:
                    print("BREAKING")
                    break
                else:
                    self.update_status(path)

    def initialized(self):
        return self.is_initialized

    def kill(self):
        self.active = False
        self.popen.terminate()

