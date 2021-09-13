# coding=utf-8
import os
import time
import subprocess

from SubscriberThread import SubscriberThread

import requests
from os.path import join

from dotenv import get_variable

from statistics import mean
from exec_cpp_thread import ExecCPPThread
import atexit

interface = "wlan0"
path_env = '/home/pi/smart-directions-slave/.env'

face_id = get_variable(path_env, 'FACE_ID')
BROKER_IP = get_variable(path_env, 'BROKER_IP')

try:
    NEIGHBOUR_MASTER = get_variable(path_env, 'NEIGHBOUR_MASTER')
except:
    NEIGHBOUR_MASTER = None

if __name__ == '__main__':
    # execute command to get our own mac address (wlan)
    command = "cat /sys/class/net/wlan0/address"

    own_mac = os.popen(command).read()
    own_mac = own_mac[:-1]
    
    # some output
    print("Running scan to find closest master...")
    
    if NEIGHBOUR_MASTER is None:
        # executes a scan for BLE values
        command = "sudo timeout 20s btmon"
        process = os.popen(command)
        output = process.read()
        process.close()
        
        results = output.split("HCI Event: ")
        results = list(filter(lambda x: "raspberryp" in x, results))

        dict_sniffed = {}   # we build a mapping [{mac, ssid, rssi}] to be localized via the fingerprinting
        
        for r in results:
            mac_length = 17
            mac = r.split("Address: ")[1][:mac_length]
            rssi = r.split("RSSI: ")[1].split(" dBm")[0]
            
            if mac in dict_sniffed:
                dict_sniffed[mac].append(int(rssi))
            else:
                dict_sniffed.update({mac: []})
        
        dict_sniffed = {mac: mean(dict_sniffed[mac]) for mac in dict_sniffed.keys()}

        max_rssi = float("-inf")
        best_mac = None
        for mac in dict_sniffed.keys():
            if dict_sniffed[mac] > max_rssi:
                max_rssi = dict_sniffed[mac]
                best_mac = mac
        assert best_mac is not None, "No master has been found"
    else:
        print("Taking master from .env")
        best_mac = NEIGHBOUR_MASTER

    print("INFO: Paired with: {}".format(best_mac))
    
    exec_cpp_thread = ExecCPPThread()
    exec_cpp_thread.start()

    atexit.register(exec_cpp_thread.kill)

    while not exec_cpp_thread.initialized():
        print("Wait for init...")
        time.sleep(5)
        
    SubscriberThreadInstance = SubscriberThread(best_mac.lower(), own_mac, face_id, BROKER_IP)
    SubscriberThreadInstance.start()
    

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
