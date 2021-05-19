# coding=utf-8
import os
import time
import subprocess

from SubscriberThread import SubscriberThread

import requests
from os.path import join

from dotenv import get_variable

from ping_thread import PingThread

from statistics import mean

interface = "wlan0"
path_env = '/home/pi/smart-directions-slave/.env'

base_path_scanner = get_variable(path_env, 'BASE_PATH_SCANNER')
assets_path_scanner = join(base_path_scanner, get_variable(path_env, 'RELATIVE_PATH_ASSETS'))
face_id = get_variable(path_env, 'FACE_ID')
BROKER_IP = get_variable(path_env, 'BROKER_IP')

if __name__ == '__main__':
    # execute command to get our own mac address (wlan)
    command = "cat /sys/class/net/wlan0/address"

    own_mac = os.popen(command).read()
    own_mac = own_mac[:-1]

    # executes a scan for BLEI values
    #command = "sudo btmon" #"iw dev {} scan".format(interface)
    command = "sudo timeout 10s btmon"
    process = os.popen(command)
    output = process.read()
    process.close()
    #time.sleep(10)
    print(output)
    results = output.split("HCI Event: ")
    results = list(filter(lambda x: "raspberryp" in x, results))

    dict_sniffed = {}   # we build a mapping [{mac, ssid, rssi}] to be localized via the fingerprinting
    
    print(results,"\n\t")
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
    assert best_mac is not None, "Not found"
    print(dict_sniffed)

    print("I AM THE BEEEEST {}".format(best_mac))

    SubscriberThreadInstance = SubscriberThread(best_mac, own_mac, face_id, BROKER_IP)
    SubscriberThreadInstance.start()

    print("ENDED")
    

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
