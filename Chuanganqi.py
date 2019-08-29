# -*- coding:utf-8 -*-
import OPi.GPIO as GPIO
import time
import os
import smbus
import glob
import json
from ctypes import *


class DS18b20(object):#水温探头类
    def __init__(self,DateModel):
        self.DateModel=DateModel
        self.base_dir = '/sys/bus/w1/devices/'
        try:
            self.device_status=True
            self.device_folder = glob.glob(self.base_dir + '28*')[0]
            self.device_file = self.device_folder + '/w1_slave'
        except Exception,e:
            print e
			self.device_status=False
    def read_temp_raw(self):
        if self.device_status==True:
            f = open(self.device_file, 'r')
            lines = f.readlines()
            f.close()
            return lines
        else:
			return False

    def start(self):
		lines = self.read_temp_raw()
        while lines!=False and lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        if lines!=False:
            equals_pos = lines[1].find('t=')
            if equals_pos != -1: 
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                #temp_f = temp_c * 9.0 / 5.0 + 32.0
                self.DateModel.watertemp='%.1f'%temp_c
                #return temp_c
        else:
            self.DateModel.watertemp=0
class GuangZhao(object):#光照传感器
    def __init__(self,DateModel):
        self.DateModel=DateModel
        self.bus = smbus.SMBus(1)
        self.addr = 0x23
    def start(self):
        try:
            data = self.bus.read_i2c_block_data(self.addr,0x11)
            value=int((data[1] + (256 * data[0])) / 1.2)
            self.DateModel.Light=value
        except Exception,e:
            print e
            self.DateModel.Light=0
            
class DHT11(object):
    def __init__(self,DateModel):
        self.DateModel=DateModel
        self.so = cdll.LoadLibrary
        self.wenshidu = self.so('/root/demo/wenshidu.so')
        self.wenshidu.dht11_read_val.restype = c_char_p
        self.wenshidu.init()
    def start(self):
        try:
            data = self.wenshidu.dht11_read_val()
            #print("dht11:"+str(data))
            if not data=="false":#温湿度
                dataJson=json.loads(data)#温湿度
                self.DateModel.Temp=dataJson["temp"]#温湿度
                self.DateModel.humidity=dataJson["humidity"]#温湿度
        except Exception,e:
            print e
            self.DateModel.Temp=0#温湿度
            self.DateModel.humidity=0#温湿度