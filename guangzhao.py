#!/usr/bin/python
# -*- coding:utf-8 -*-
#import OPi.GPIO as GPIO
import time
import smbus
import dataClass as DataClass
bus=None
addr=None
def init():
    global bus
    global addr
    print "打开光照传感器"
    bus = smbus.SMBus(1)
    addr = 0x23
    DataClass._init()
    DataClass.set_value("lightStatus",1)
def start():
    global bus
    global addr
    data = bus.read_i2c_block_data(addr,0x11)
    value=int((data[1] + (256 * data[0])) / 1.2)
    DataClass.set_value("Light",value)
    time.sleep(2)
	
