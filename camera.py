#!/usr/bin/python
# -*- coding:utf-8 -*-
from socketIO_client import SocketIO
#import logging
import cv2
import time
import Image
import StringIO
import mysql as Mysql
import numpy
import threading

#logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
#logging.basicConfig()
global socketIO
global loop
loop=1
img_quality = 10#设置摄像头的质量，越高越流畅，但资源消耗越大，越容易出问题
resolution = (640, 480)#设置图像分辨率
def on_connect():
    print('connect')


def on_disconnect():
    print('disconnect')

def on_reconnect():
    print('reconnect')

def on_response(*args):
    global loop
    message=str(args[0])
    print(str(message))
    if message=="open":
        loop=1
        t1 = threading.Thread(target=getCamera)
        t1.start()
        #getCamera()
    if message=="closed":
        loop=0
def on_close(*args):
    print('client is close...')
    global loop
    loop=0
def getCamera():
    global loop
    # 获取摄像头
    dev_num=0
    cap = cv2.VideoCapture(dev_num)
    # 调整采集图像大小为640*480
    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),img_quality]
    while (loop):
        # 获取一帧图像
        (ret, img) = cap.read()
        # 如果ret为false，表示没有获取到图像，退出循环
        if ret is False:
            if dev_num==0:
                dev_num=1
                print("video_num is 1")
            elif dev_num==1:
                dev_num=0
                print("video_num is 0")
            cap = cv2.VideoCapture(dev_num)
            continue
        img  = cv2.resize(img,resolution)
        result, imgencode = cv2.imencode('.jpg',img,encode_param)
        img_code = numpy.array(imgencode)        
        imgdata  = img_code.tostring()
        socketIO.emit("camera",imgdata.encode("base64"))# 通过socket传到服务器
        time.sleep(0.1)
    cap.release()
Mysql.setDb()
productId=Mysql.select("select devicenum from info ")[0]
print(str(productId))
socketIO=SocketIO('112.74.52.38', 9000 , params={'poster': str(productId),'type':'0'})
socketIO.on('connect', on_connect)
socketIO.on('disconnect', on_disconnect)
socketIO.on('reconnect', on_reconnect)
socketIO.on('response', on_response)
socketIO.on('close', on_close)
socketIO.wait()#wait()方法不带参数代表无限循环等待，带参数则等待数值的时间后关闭连接



