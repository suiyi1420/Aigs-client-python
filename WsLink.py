#!/usr/bin/python
# -*- coding:utf-8 -*-
import websocket
import time
import threading
import urllib
import commonFun

class WsLink(threading.Thread):
    
    def __init__(self,DateModel,Food):
        super(WsLink, self).__init__()
        self.DateModel=DateModel
        self.Food=Food
        self.url = ("ws://www.fallwings.top/aigs/websocket/socketServer?deviceNum="+str(self.DateModel.productId))
        self.ws =None
        
    def on_message(self,message):
        print(message)
        commonFun.getFromWeb(self,message)

    def on_error(self,error):
        print(error)

    def on_close(self):
        print("### closed ###")
        self.DateModelwebSocketStatus=0
        self.DateModel.ws=None
        self.DateModel.isSend=False
        
    def on_open(self):
        print("webSocket starting...")
        self.DateModel.webSocketStatus=1
        self.DateModel.ws=self.ws
        msg={"msg":'connect'}
        self.sendMessage(str(msg))
        
    def sendMessage(self,message):
        self.ws.send(message)

    def run(self):
        ping_code=0
        while ping_code!=200:
            try:
                ping_code = urllib.urlopen("http://www.fallwings.top/aigs").code#ping网络，看是否联通，联通才打开通道
                print ("ping_code:"+str(ping_code))
            except Exception,e:
                print e
            time.sleep(5)
        if ping_code==200:
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(self.url,on_close=self.on_close,on_error=self.on_error,on_message=self.on_message)
            self.ws.on_open=self.on_open
            self.ws.run_forever()
    

        