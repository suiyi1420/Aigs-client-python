#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

def setWifi(ssid,password):
    cmd=["source /etc/network/interfaces.d/*\n","auto wlan0\n","allow-hotplug wlan0\n","iface wlan0 inet dhcp\n",'wpa-ssid "'+ssid+'"\n','wpa-psk "'+password+'"\n']
    f1 = open('/etc/network/interfaces', 'w')
    f1.writelines(cmd)
    f1.close()
    os.system("reboot")