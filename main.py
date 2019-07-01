#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import OPi.GPIO as GPIO
import time
import threading
import websocket
import socket
import guangzhao
import guangzhao
#import turanshidu
import watertemp
import wifi
import food as Food
import json
import dataClass as DataClass
import kongzhiqi
import mysql as Mysql
import threading
import json
import urllib
import os
import zipfile
import datetime
import multiprocessing
from ctypes import *
so = cdll.LoadLibrary
wenshidu = so('/root/demo/wenshidu.so')
wenshidu.dht11_read_val.restype = c_char_p
wenshidu.getData.restype = c_char_p
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
global ws,productId,version
ws=None
productId='0'
version="1.4.0.3"
t1=None
t2=None
isSend=False
GPIO.setup(12, GPIO.OUT)
#GPIO.setup(13, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(12, GPIO.LOW)
GPIO.output(8, GPIO.LOW)
GPIO.output(15, GPIO.LOW)
GPIO.output(19, GPIO.LOW)
GPIO.output(21, GPIO.LOW)
def guangzhaoStart():
    def run(*args):
        guangzhao.init()
    thread.start_new_thread(run, ())
def sendMessage(ws,message):
    ws.send(str(message))
def on_message(ws,message):
    global version
    global isSend
    print(message)
    obj = json.loads(message)
    type = obj['msg']
    if type == 'connect':#手机端与硬件建立连接后，手机端发送connect指令，则获取硬件当前的状态，若当前为手动控制，则获取硬件各传感器和控制器的状态，同时发送connect指令给手机端
        msg={"msg":'connect'}
        ws.send(str(msg))
    if type == 'isSend':#手机端与硬件建立连接后，手机端发送connect指令，则获取硬件当前的状态，若当前为手动控制，则获取硬件各传感器和控制器的状态，同时发送connect指令给手机端
        issen=obj['isSend']
        if issen=="0":
            isSend=False
        else:
            isSend=True
    if type == 'change':#手机端与硬件建立连接后，手机端发送connect指令，则获取硬件当前的状态，若当前为手动控制，则获取硬件各传感器和控制器的状态，同时发送connect指令给手机端
        #msg={"msg":'connect'}
        #ws.send(str(msg))
        
        DataClass.set_value("autoClock",int(obj['value']))
        Mysql.setDb()
        Mysql.update(str("update device set status="+obj['value']+" where name='autoClock'"))
        Mysql.closeDb()   
    if type == 'set':#手机端发送change指令，则获取指令中的key值(需要改变的控制器)和对应的value值(改变的值是多少)，若为autoClock,则改变控制类型(自动、手动)。
        setDevice(obj)
    if type == 'changeDevice':#手机端发送changeDevice指令，改变控制器的状态,status:0-->关闭，1-->打开
        typ=obj['type']
        stat=obj['status']
        changeDevice(typ,stat)
    if type == 'setWifi':#手机端发送setWifi指令，设置WIFI帐号密码
        ssid=obj['ssid']
        password=obj['password']
        wifi.setWifi(ssid,password)
    if type == 'changeAuto':#手机端发送changeAuto指令，改变自动控制的各个传感器的自动控制状态
        typ=obj['type']
        stat=obj['status']
        changeAuto(typ,stat)
    if type == 'resetCamera':#手机端发送changeAuto指令，改变自动控制的各个传感器的自动控制状态
        os.system("systemctl restart camera")
    if type == 'addFoodTime':#手机端发送addFoodTime指令，添加自动喂食时间
        ftimeList=obj['list']
        Food.addTime(ftimeList)
    if type == 'setFoodSpeed':#手机端发送setFoodSpeed指令，设置自动喂食持续时间和速度
        ffood_speed=int(obj['food_speed'])
        ffood_chixu_time=int(obj['food_chixu_time'])
        Food.setSpeed(ffood_speed,ffood_chixu_time)
    if type == 'deleteFoodTime':#手机端发送deleteFoodTime指令，删除自动喂食时间
        deleteId=obj['id']
        Food.deleteTime(deleteId)
    if type == 'food_time_list':#手机端发送获取喂食时间列表指令
        msg={"msg":'food_time_list',"list":Food.getList()}
        ws.send(str(msg))
    if type == 'sysTime':#服务端发送更新系统时间指令
        sysTime=obj['sysTime']
        print("服务器时间："+str(sysTime))
        os.system('date -s "'+sysTime+'"')
        setTomorrow()
    if type == 'update':#手机端发送update指令，检查硬件代码与云端的版本号是否一致，不一致则下载云端的最新代码，并提示重启应用
        version_could=obj['version']
        print("云端版本："+str(version_could))
        def Schedule(a,b,c):
            per = 100.0 * a * b / c
            print '%.2f%%' % per
        if version!=version_could:
            url = 'http://www.fallwings.top/aigs/file/demo.zip'
            local = os.path.join('/root/','demo.zip')
            urllib.urlretrieve(url,local,Schedule)
            if ws is not None:
                msg={"msg":'update'}
                print str(msg)
                ws.send(str(msg))
            azip = zipfile.ZipFile('/root/demo.zip')
            azip.extractall("/root/demo/")
            os.system("reboot")



def on_error(ws,error):
    print(error)
    #WsInit()
    #ws=None
    #while not ws:
    #    WsInit()

def on_close(ws):
    global isSend
    print("### closed ###")
    DataClass.set_value("webSocketStatus",0)
    msg={"msg":"close"}
    #ws.send(str(msg))
    #global ws
    ws=None
    isSend=False
    #DataClass.set_value("ws",None)
    #WsInit()


def on_open(ws):
    DataClass.set_value("webSocketStatus",1)
    DataClass.set_value("ws",ws)
    msg={"msg":"connect"}
    ws.send(str(msg))
    print("webSocket starting...")
    

#websocket初始化
def WsInit():
    global productId
    global ws
    #global IP

    #productId=DataClass.get_value("productId")
    #print ("productId:"+productId)
    ping_code=0
    while ping_code!=200:
        try:
            ping_code = urllib.urlopen("http://www.fallwings.top/aigs").code#ping网络，看是否联通，联通才打开通道
        except Exception,e:
            print e
        time.sleep(5)
    if ping_code==200:
        os.system("systemctl start camera.service")#网络连通后启动摄像头服务
        websocket.enableTrace(False)#该方法，True表示追踪websocket链接的信息，类似debug日志，False则不追踪
        ws = websocket.WebSocketApp("ws://www.fallwings.top/aigs/websocket/socketServer?deviceNum="+str(productId),on_message = on_message,on_error = on_error,on_close = on_close)
        #ws = websocket.WebSocketApp("ws://192.168.1.30:8080/designer-remote/websocket/socketServer?deviceNum="+str(productId),on_message = on_message,on_error = on_error,on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()

        #IP=get_host_ip()

#获取本机IP地址
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

#初始化数值，从数据库读取，每次启动应用都先执行
def init():
    DataClass._init()
    Mysql.setDb()
    
    #print ('productId:'+DataClass.get_value("productId"))
    
#循环监听
def loop():
    global ws
    global t2
    global isSend
    while True:
    #turanshidu.init()
        if t2 is not None :
            if t2.is_alive():
                print("ws is alive")
            else:
                print("ws is be killed,restarting...")
                t2 = threading.Thread(target=WsInit)
                t2.start()
        try:
            guangzhao.start()
            watertemp.readtemperature()
            wenshiduString=wenshidu.dht11_read_val()#温湿度
            if not wenshiduString=="false":#温湿度
                wenshiduJson=json.loads(wenshiduString)#温湿度
                DataClass.set_value("Temp",wenshiduJson["temp"])#温湿度
                DataClass.set_value("humidity",wenshiduJson["humidity"])#温湿度
            #if turanshidu.start()=="0":
            #    DataClass.set_value("turanshidu",0)#土壤湿度
            #if turanshidu.start()=="1":
            #    DataClass.set_value("turanshidu",1)#土壤湿度

            if DataClass.get_value("autoClock")==1 or DataClass.get_value("autoClock")=="1":
                autoControl()
            msg={"msg":"get","list":{"light":str(DataClass.get_value("Light")),"temp":str(DataClass.get_value("Temp")),
"humidity":str(DataClass.get_value("humidity")),"watertemp":str(DataClass.get_value("watertemp")),
"critical":{"lamp":{"min":str(DataClass.get_value("min_lamp")),"max":str(DataClass.get_value("max_lamp"))},
"temp":{"min":str(DataClass.get_value("min_temp")),"max":str(DataClass.get_value("max_temp"))},
"humidity":{"min":str(DataClass.get_value("min_humidity")),"max":str(DataClass.get_value("max_humidity"))},
"watertemp":{"min":str(DataClass.get_value("min_watertemp")),"max":str(DataClass.get_value("max_watertemp"))},
"food":{"food_speed":DataClass.get_value("food_speed"),"food_running_time":DataClass.get_value("food_running_time"),"food_chixu_time":DataClass.get_value("food_chixu_time")}},
"status":{"lamp":str(DataClass.get_value("light_status")),"watertemp":str(DataClass.get_value("watertemp_status")),
"penshui":str(DataClass.get_value("penshui_status")),"temp":str(DataClass.get_value("tempStatus"))},
"auto":{"autoClock":str(DataClass.get_value("autoClock")),"temp_auto":str(DataClass.get_value("temp_auto")),"lamp_auto":str(DataClass.get_value("lamp_auto")),
"humidity_auto":str(DataClass.get_value("humidity_auto")),"watertemp_auto":str(DataClass.get_value("watertemp_auto")),"food_auto":str(DataClass.get_value("food_auto"))}}}
            #print str(msg)
            print ("webSocketStatus:"+str(DataClass.get_value("webSocketStatus")))
            if DataClass.get_value("webSocketStatus")==1 and isSend==True:
              #  if ws != None:
                sendMessage(ws,msg)
            time.sleep(1)
        except KeyboardInterrupt:
            pass
    GPIO.cleanup()

#修改设备的监控范围
def setDevice(obj):
    min=obj["min"]
    max=obj["max"]
    device=obj["device"]
    DataClass.set_value(str("min_"+device),min)
    DataClass.set_value(str("max_"+device),max)
    sql=str("update device set min_value="+min+",max_value="+max+" where name='"+device+"'")
    print sql
    Mysql.setDb()
    Mysql.update(sql)
    Mysql.closeDb()

def changeAuto(type,status):
    DataClass.set_value(str(type),status)
    sql=str("update device set status="+status+" where name='"+type+"'")
    print sql
    Mysql.setDb()
    Mysql.update(sql)
    Mysql.closeDb()

#手动改变控制器状态
def changeDevice(type,status):
    print str(type)
    
    if status=='0' or status==0:
        #penshui.close(type)
        kongzhiqi.close(str(type))
        if type=='penshui_pin':
            DataClass.set_value("penshui_status",0)
        if type=='lamp_pin':
            DataClass.set_value("light_status",0)
        if type=='food_pin':
            DataClass.set_value("food_status",0)
        if type=='watertemp_pin':
            DataClass.set_value("watertemp_status",0)
        if type=='temp_pin':
            DataClass.set_value("tempStatus",0)
    if status=='1' or status==1:
        if type=='food_pin':
            Food.food_run()
        else:
            kongzhiqi.open(str(type))
            if type=='penshui_pin':
                DataClass.set_value("penshui_status",1)
            if type=='lamp_pin':
                DataClass.set_value("light_status",1)
            if type=='food_pin':
                DataClass.set_value("food_status",1)
            if type=='watertemp_pin':
                DataClass.set_value("watertemp_status",1)
            if type=='temp_pin':
                DataClass.set_value("tempStatus",1)

#自动控制控制器状态
def autoControl():
    Temp=int(DataClass.get_value("Temp"))
    min_temp=int(DataClass.get_value("min_temp"))
    max_temp=int(DataClass.get_value("max_temp"))
    humidity=int(DataClass.get_value("humidity"))
    min_humidity=int(DataClass.get_value("min_humidity"))
    max_humidity=int(DataClass.get_value("max_humidity"))
    #turanshidu=DataClass.get_value("turanshidu")
    Light=int(DataClass.get_value("Light"))
    min_lamp=int(DataClass.get_value("min_lamp"))
    max_lamp=int(DataClass.get_value("max_lamp"))
    watertemp=int(DataClass.get_value("watertemp"))
    min_watertemp=int(DataClass.get_value("min_watertemp"))
    max_watertemp=int(DataClass.get_value("max_watertemp"))
############################################
    if DataClass.get_value("temp_auto")==1 or DataClass.get_value("temp_auto")=="1":#空气加温
        #if Temp>max_temp :
            #kongzhiqi.open("penshui_pin")
            #DataClass.set_value("penshui_status",1)
        #    kongzhiqi.close("temp_pin")
        if Temp<min_temp:
            #kongzhiqi.close("penshui_pin")
            #DataClass.set_value("penshui_status",0)
            kongzhiqi.open("temp_pin")
            DataClass.set_value("tempStatus",1)
        else:
            kongzhiqi.close("temp_pin")
            DataClass.set_value("tempStatus",0)
            #if DataClass.get_value("humidity_status")==0:
            #    kongzhiqi.close("penshui_pin")
            #   DataClass.set_value("penshui_status",0)
    #else:
    #    kongzhiqi.close("temp_pin")
    #    if DataClass.get_value("humidity_status")==0:
    #        kongzhiqi.close("penshui_pin")
    #        DataClass.set_value("penshui_status",0)
############################################
    if DataClass.get_value("lamp_auto")==1 or DataClass.get_value("lamp_auto")=="1":#电灯
        if Light<min_lamp:
            kongzhiqi.open("lamp_pin")
            DataClass.set_value("light_status",1)
        else:
            kongzhiqi.close("lamp_pin")
            DataClass.set_value("light_status",0)
    #else:
    #    kongzhiqi.close("lamp_pin")
    #    DataClass.set_value("light_status",0)
#################################################
    if DataClass.get_value("humidity_auto")==1 or DataClass.get_value("humidity_auto")=="1":#湿度
        if humidity<min_humidity:
            kongzhiqi.open("penshui_pin")
            DataClass.set_value("penshui_status",1)
            DataClass.set_value("humidity_status",1)
        else:
            kongzhiqi.close("penshui_pin")
            DataClass.set_value("penshui_status",0)
            DataClass.set_value("humidity_status",0)
    #else:
    #    kongzhiqi.close("penshui_pin")
     #   DataClass.set_value("penshui_status",0)
    #    DataClass.set_value("humidity_status",0)
#########################################
    if DataClass.get_value("watertemp_auto")==1 or DataClass.get_value("watertemp_auto")=="1":#水湿度
        if watertemp<min_watertemp:
            kongzhiqi.open("watertemp_pin")
            DataClass.set_value("watertemp_status",1)
        else:
            kongzhiqi.close("watertemp_pin")
            DataClass.set_value("watertemp_status",0)
    #else:
    #    kongzhiqi.close("watertemp_pin")
    #    DataClass.set_value("watertemp_status",0)
    #print(int(DataClass.get_value("food_auto")))
    if int(DataClass.get_value("food_auto"))==1:#湿度
        Food.start()
        
def setTomorrow():#设置明天的日期
    next_time_date=datetime.date.fromordinal(datetime.date.today().toordinal() + 1)#明天的日期
    DataClass.set_value("next_time_date",next_time_date)
    #print("明天时间:"+str(DataClass.get_value("next_time_date")))
#程序主函数
if __name__ == "__main__":
    global productId
    global t1
    global t2
    DataClass._init()
    Mysql.setDb()
    productId=Mysql.select("select devicenum from info ")[0]
    DataClass.set_value("productId",productId)
    Mysql.closeDb()
    guangzhao.init()
    wenshidu.init()
    Food.setup()
    kongzhiqi.close("temp_pin")#初始化所有继电器未关闭状态
    kongzhiqi.close("lamp_pin")
    kongzhiqi.close("penshui_pin")
    kongzhiqi.close("watertemp_pin")
    setTomorrow()
    #print ('productId:'+productId)
    Food.countTime()#初始化执行一次喂食列表
    
    if not productId=='0':
        t2 = threading.Thread(target=WsInit)
        t1 = threading.Thread(target=loop)
        #time.sleep(1)        
        t2.start()
        time.sleep(1)
        t1.start()
        t1.join() 
        t2.join()

        

    GPIO.cleanup()

    
    
    
