#!/usr/bin/python
#coding=utf-8

import OPi.GPIO as GPIO
import time
import datetime
import mysql as Mysql
import json
import socketio
import multiprocessing

class Food():
    def __init__(self,DateModel):
        self.weekObject={"0":"日","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六"}
        self.DateModel=DateModel
    def getWeek(self,week):
        return self.weekObject[week]

    def setStep(self,w1, w2, w3, w4):
        GPIO.output(self.DateModel.food_pin1, w1)
        GPIO.output(self.DateModel.food_pin2, w2)
        GPIO.output(self.DateModel.food_pin3, w3)
        GPIO.output(self.DateModel.food_pin4, w4)
 
    def food_stop(self):
        self.setStep(0, 0, 0, 0)
        self.DateModel.food_status=1
 
    def quick(self,delay):  #高速
        self.setStep(0, 0, 0, 1)
        time.sleep(delay)
        self.setStep(0, 0, 1, 0)
        time.sleep(delay)
        self.setStep(0, 1, 0, 0)
        time.sleep(delay)
        self.setStep(1, 0, 0, 0)
        time.sleep(delay)
     
    def low(self,delay):  #低速
        self.setStep(0, 0, 0, 1)
        time.sleep(delay)
        self.setStep(0, 0, 1, 1)
        time.sleep(delay)
        self.setStep(0, 0, 1, 0)
        time.sleep(delay)
        self.setStep(0, 1, 1, 0)
        time.sleep(delay)
        self.setStep(0, 1, 0, 0)
        time.sleep(delay)
        self.setStep(1, 1, 0, 0)
        time.sleep(delay)
        self.setStep(1, 0, 0, 0)
        time.sleep(delay)
        self.setStep(1, 0, 0, 1)
        time.sleep(delay)
 
 
    def food_run(self):#喂食启动，开启新的进程
        chixutime=int(self.DateModel.food_chixu_time)
        food_speed=int(self.DateModel.food_speed)
        ws=self.DateModel.ws
        webSocketStatus=self.DateModel.webSocketStatus
        isSend=self.DateModel.isSend
        def running(ws,chixutime,food_speed,webSocketStatus,isSend):
            t=time.time()
            if ws is not None and webSocketStatus=="1" and isSend==True:
                msg={"msg":'food_status',"food_status":1}
                print("not none")
                ws.send(str(msg))
            while int(time.time()-t)<=chixutime:#计算运行时间
                print(str(int(time.time()-t)))
                if int(food_speed)==0:
                    self.low(0.002)
                elif int(food_speed)==1:
                    self.quick(0.002)  # 512 steps --- 360 angle
            self.food_stop()#时间结束后停止喂食
            if ws is not None and webSocketStatus=="1" and isSend==True:
                print("food_status:0")
                msg={"msg":'food_status',"food_status":0}
                ws.send(str(msg))
        m1 = multiprocessing.Process(target=running,args=(ws,chixutime,food_speed,webSocketStatus,isSend))
        m1.start()
            


    def addTime(self,timeJson):
        for item in timeJson:
            sql="insert into log values('"+item['id']+"','"+item['time']+"','"+item['week']+"')"
            #print(sql)
            Mysql.setDb()
            Mysql.insert(sql)
            Mysql.closeDb()
        self.countTime()#刷新时间列
    #设置喂食速度
    def setSpeed(self,ffood_speed,ffood_chixu_time):
        self.DateModel.food_chixu_time=ffood_chixu_time
        self.DateModel.food_speed=ffood_speed
        #print("ffood_speed:"+str(self.DateModel.food_chixu_time))
        sql1="update device set min_value='"+str(ffood_speed)+"' where name='food_speed'"
        sql2="update device set min_value='"+str(ffood_chixu_time)+"' where name='food_chixu_time'"
        Mysql.setDb()
        Mysql.insert(sql1)
        Mysql.insert(sql2)
        Mysql.closeDb()

    def deleteTime(self,id):
        Mysql.setDb()
        Mysql.delete("delete from log where name='"+id+"'")
        Mysql.closeDb()
        self.countTime()#刷新时间列

    def getList(self):#获取喂食的时间列
        result=[]
        Mysql.setDb()
        list=Mysql.selectList("select * from log where name like 'food%' order by value , createtime asc")
        Mysql.closeDb()
        if list:
            for t in list:
                #print t[0]
                result.append({"id":t[0],"time":t[1],"week":t[2]})
        return result
            
    def countTime(self):#获取当天需要喂食的时间列
        print("countTime")
        list=self.getList()
        nowWeek=int(time.strftime("%w")) #当前星期几
        nowHour=int(time.strftime("%H"))
        nowMinute=int(time.strftime("%M"))
        rList=[]
        next_time_flag=True
        for t in list:#循环遍历匹配当天需要喂食的时间
            sttr=t["time"]
            tT=sttr.split(":")
            tHour=int(tT[0])
            tMinute=int(tT[1])
            if int(t["week"]) == nowWeek:
                rList.append(t)
                if (int(tHour) == nowHour and int(tMinute)>nowMinute) or (int(tHour) > nowHour) :
                    if next_time_flag:
                        self.DateModel.food_running_time={"week":t["week"],"time":t["time"]}#记录当前正在喂食
                        print("下次喂食时间："+str(self.DateModel.food_run_time_list))
                        next_time_flag=False
            
        if next_time_flag:
            self.DateModel.food_running_time="0"
        self.DateModel.food_run_time_list=rList
            
    def start(self):
        nowTime= datetime.date.today()
        nowHour=int(time.strftime("%H"))
        nowMinute=int(time.strftime("%M"))
        nextday=self.DateModel.next_time_date#明天的日期
        differenceValue=(nextday-nowTime).days#明天的日期与今天的日期相减，判断当前的日期是否已经到了明天，值为0则表示到了第二天
        #print("当前时间:"+str(nowTime))
        #print("明天时间2:"+str(nextday))
        #print("时间差:"+str(differenceValue))
        if differenceValue==0:#当前日期已是第二天，明天日期需更新
            self.DateModel.next_time_date=datetime.date.today()+datetime.timedelta(days=1)
            self.countTime()#获取当天需要喂食的时间列
        list=self.DateModel.food_run_time_list
        #print(list)
        if len(list)>0:#当天有喂食时间
            for t in list:#循环遍历匹配当天需要喂食的时间
                tT=t["time"].split(":")
                tHour=int(tT[0])
                tMinute=int(tT[1])
                if tHour==nowHour and tMinute==nowMinute:
                    list.remove(t)
                    self.DateModel.food_run_time_list=list
                    print("*******************\n")
                    print(self.DateModel.food_run_time_list)
                    food_run()
                    break

    
