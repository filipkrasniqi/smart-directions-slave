# coding=utf-8
# This is a sample Python script.
import os
import subprocess

import requests
from os.path import join

from dotenv import get_variable

# TODO pushare tutto, runnare le singole ancore
FLASK_URL = get_variable('.env', 'FLASK_URL')

interface = "wlan0"
base_path_scanner = "/home/pi/ble_scanner/"
assets_path_scanner = join("/home/pi/ble_scanner/", 'assets')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    command = "iw dev {} scan".format(interface)
    output = os.popen(command).read()
    results = output.split("BSS ")
    results = list(filter(lambda x: "wlan0)" in x, results))
    dict_sniffed = []
    for r in results:
        lines = r.split("\n\t")
        mac = lines[0].replace("(on wlan0)", "")#re.sub("\(on wlan0\)", '', lines[0])
        rssi = float(lines[6].replace("signal: ", "").replace(" dBm", ""))
        ssid = lines[8].replace("SSID: ", '')
        #if "TIM-23" in ssid or "TP-LINK" in ssid or "KA" in ssid:
        dict_sniffed.append({'mac': mac, 'ssid': ssid, 'rssi': rssi})

    command = "cat /sys/class/net/wlan0/address"

    try:
        with open(join(assets_path_scanner, "node.setup"), 'r') as file:
            id_sd = int(file.readline())
    except:
        print("WARNING: wrong")
        exit(0)

    data = {'id_sd': id_sd, 'wifi': dict_sniffed}

    own_mac = os.popen(command).read()
    r = requests.post("{}{}/init".format(FLASK_URL, own_mac), json=data)
    response = r.json()
    id_node, id_building = response['id_node'], response['id_building']
    file_info_path = join(assets_path_scanner, "node.info")
    try:
        with open(file_info_path, 'w') as file:
            file.write(str(id_node))
            file.close()
    except Exception as e:
        print("ERROR: not able to write {}".format(e))
        exit(0)

    print("SUCCESS: init went fine. Starting to scan")
    print()
    print()
    command = join(base_path_scanner, "cmake-build-rasp1/ble_scanner")
    # running c++
    process = subprocess.Popen([command])
    process.wait()

    print("ENDED")



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
