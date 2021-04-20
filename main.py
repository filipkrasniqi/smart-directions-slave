# coding=utf-8
import os

import requests
from os.path import join

from dotenv import get_variable

from ping_thread import PingThread

FLASK_URL = get_variable('.env', 'FLASK_URL')

interface = "wlan0"
base_path_scanner = get_variable('.env', 'BASE_PATH_SCANNER')
assets_path_scanner = join(base_path_scanner, get_variable('.env', 'RELATIVE_PATH_ASSETS'))

if __name__ == '__main__':
    # execute command to get our own mac address (wlan)
    command = "cat /sys/class/net/wlan0/address"

    own_mac = os.popen(command).read()
    own_mac = own_mac[:-1]

    # executes a scan for WIFI RSSI values
    command = "iw dev {} scan".format(interface)
    output = os.popen(command).read()
    results = output.split("BSS ")
    results = list(filter(lambda x: "wlan0)" in x, results))
    dict_sniffed = []   # we build a mapping [{mac, ssid, rssi}] to be localized via the fingerprinting
    for r in results:
        lines = r.split("\n\t")
        mac = lines[0].replace("(on wlan0)", "")#re.sub("\(on wlan0\)", '', lines[0])
        rssi = float(lines[6].replace("signal: ", "").replace(" dBm", ""))
        ssid = lines[8].replace("SSID: ", '')
        #if "TIM-23" in ssid or "TP-LINK" in ssid or "KA" in ssid:
        dict_sniffed.append({'mac': mac, 'ssid': ssid, 'rssi': rssi})

    # get id of the SD instance to which we currently refer to
    try:
        with open(join(assets_path_scanner, "node.setup"), 'r') as file:
            id_sd = int(file.readline())
    except:
        print("WARNING: wrong")
        exit(0)

    file_info_path = join(assets_path_scanner, "node.info")
    # if needed, init the anchor
    try:
        with open(file_info_path, 'r') as file:
            id_node = int(file.readline())
    except:
        print("WARNING: init required")

        # build body for request
        data = {'id_sd': id_sd, 'wifi': dict_sniffed}
        r = requests.post("{}{}/init".format(FLASK_URL, own_mac), json=data)
        response = r.json()
        id_node, id_building = response['id_node'], response['id_building']
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

    # start timer executing ping thread: we check server is alive and eventually execute sniffer code
    ping_scheduler = PingThread('Ping', own_mac)
    ping_scheduler.start()

    print("ENDED")


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
