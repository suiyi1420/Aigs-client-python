#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import threading
import LEDDrivers
import Food
import DateModel 
from Chuanganqi import DS18b20,GuangZhao,DHT11
from WsLink import WsLink
from web.web import Web


wsLink=None
webApp=None
dateModel=None
food=None
		
		
#循环执行
def loop(dateModel,food,ds18b20,guangZhao,dht11,led):
    global wsLink
    global webApp
    while True:
        
        dateModel.get_host_ip()
        guangZhao.start()
        dht11.start()
        ds18b20.start()
        led.setDraw()
        if str(dateModel.autoClock)=="1":
            dateModel.autoControl(food)
        sendData=str(dateModel.getMapDate())
        #print(sendData)
        
        if wsLink is not None :
            if wsLink.is_alive():
                #print("ws is alive")
                if str(dateModel.webSocketStatus)=="1" and dateModel.isSend==True and dateModel.ws is not None:
                    wsLink.sendMessage(sendData)
            else:
                print("ws is be killed,restarting...")
                wsLink = WsLink(dateModel,food)
                wsLink.start()
        if webApp is not None :
            if webApp.is_alive():
                print("webLinkStatus:"+str(dateModel.webLinkStatus))
                if dateModel.webLinkStatus==1:
                    webApp.sendMessage(sendData)
            else:
                print("web is be killed,restarting...")
                webApp=Web(None,dateModel,food)
                webApp.start()		
        time.sleep(1)


#程序主函数
if __name__ == "__main__":
    global wsLink
    global webApp
    global dateModel
    global food
    dateModel=DateModel.DateModel()#创建数据对象
    dateModel.dateInit()#初始化数据
    ds18b20=DS18b20(dateModel)#创建水温对象
    guangZhao=GuangZhao(dateModel)#创建光找对象
    dht11=DHT11(dateModel)#创建温湿度对象
    led=LEDDrivers.LEDDrivers(dateModel)#创建led对象
    food=Food.Food(dateModel)#创建喂食对象
    food.countTime()#初始化执行一次喂食列表
    webApp=Web(None,dateModel,food)#创建内网服务对象

    #print ("webSocketStatus:"+str(dateModel.webSocketStatus))
    wsLink = WsLink(dateModel,food)#创建websocket外网连接对象
    t2 = threading.Thread(target=loop,args=(dateModel,food,ds18b20,guangZhao,dht11,led))#创建循环执行线程
    wsLink.start()
    time.sleep(1)
    webApp.start()
    t2.start()
    
    wsLink.join() 
    t2.join()
    webApp.join()



    
    
    
