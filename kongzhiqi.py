#!/usr/bin/python
# -*- coding:utf-8 -*-
import dataClass as DataClass
import OPi.GPIO as GPIO

def open(type):
    print str(type)
    GPIO.output(DataClass.get_value(type), GPIO.HIGH)#高电平触发
def close(type):
    GPIO.output(DataClass.get_value(type), GPIO.LOW)