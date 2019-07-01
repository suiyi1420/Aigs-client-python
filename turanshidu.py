#!/usr/bin/python
# -*- coding: UTF-8 -*-
import OPi.GPIO as GPIO
import time

channel = 11 #管脚7，
def init():
    global channel
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(channel, GPIO.IN)


def start():
    global channel
    if GPIO.input(channel) == GPIO.LOW:
        return "1"
    else:
        return "0"
