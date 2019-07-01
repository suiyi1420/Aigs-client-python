#!/usr/bin/python
#coding=utf-8

import OPi.GPIO as GPIO
import time
import datetime
import dataClass as DataClass
import mysql as Mysql
import json
import multiprocessing

IN1 = 23    
IN2 = 10
IN3 = 22
IN4 = 24

weekObject={"0":"日","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六"}

def getWeek(week):
    return weekObject[week]

def setStep(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)
 
def food_stop():
    setStep(0, 0, 0, 0)
    DataClass.set_value("food_status",1)
 
def quick(delay):  #高速
    setStep(0, 0, 0, 1)
    time.sleep(delay)
    setStep(0, 0, 1, 0)
    time.sleep(delay)
    setStep(0, 1, 0, 0)
    time.sleep(delay)
    setStep(1, 0, 0, 0)
    time.sleep(delay)
 
def low(delay):  #低速
    setStep(0, 0, 0, 1)
    time.sleep(delay)
    setStep(0, 0, 1, 1)
    time.sleep(delay)
    setStep(0, 0, 1, 0)
    time.sleep(delay)
    setStep(0, 1, 1, 0)
    time.sleep(delay)
    setStep(0, 1, 0, 0)
    time.sleep(delay)
    setStep(1, 1, 0, 0)
    time.sleep(delay)
    setStep(1, 0, 0, 0)
    time.sleep(delay)
    setStep(1, 0, 0, 1)
    time.sleep(delay)
 
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(IN1, GPIO.OUT)      # Set pin's mode is output
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
 
def food_run():#喂食启动，开启新的进程
    chixutime=int(DataClass.get_value("food_chixu_time"))
    food_speed=int(DataClass.get_value("food_speed"))
    ws=DataClass.get_value("ws")
    def running(ws,chixutime,speed):
        t=time.time()
        if ws is not None:
            msg={"msg":'food_status',"food_status":1}
            ws.send(str(msg))
        while int(time.time()-t)<=chixutime:#计算运行时间
            #print(str(int(time.time()-t)))
            if int(speed)==0:
                low(0.002)
            elif int(speed)==1:
                quick(0.002)  # 512 steps --- 360 angle
        food_stop()#时间结束后停止喂食
        if ws is not None:
            print("food_status:0")
            msg={"msg":'food_status',"food_status":0}
            ws.send(str(msg))            
    t3 = multiprocessing.Process(target=running,args=(ws,chixutime,food_speed,))
    t3.start()
        

    

 
def destroy():
    GPIO.cleanup()             # Release resource


def addTime(timeJson):
    for item in timeJson:
        sql="insert into log values('"+item['id']+"','"+item['time']+"','"+item['week']+"')"
        print(sql)
        Mysql.setDb()
        Mysql.insert(sql)
        Mysql.closeDb()
    countTime()#刷新时间列
#设置喂食速度
def setSpeed(ffood_speed,ffood_chixu_time):
    DataClass.set_value("food_chixu_time",int(ffood_chixu_time))
    DataClass.set_value("food_speed",int(ffood_speed))
    sql1="update device set min_value='"+str(ffood_speed)+"' where name='food_speed'"
    sql2="update device set min_value='"+str(ffood_chixu_time)+"' where name='food_chixu_time'"
    Mysql.setDb()
    Mysql.insert(sql1)
    Mysql.insert(sql2)
    Mysql.closeDb()

def deleteTime(id):
    Mysql.setDb()
    Mysql.delete("delete from log where name='"+id+"'")
    Mysql.closeDb()
    countTime()#刷新时间列

def getList():#获取喂食的时间列
    result=[]
    Mysql.setDb()
    list=Mysql.selectList("select * from log where name like 'food%' order by value , createtime asc")
    Mysql.closeDb()
    if list:
        for t in list:
            #print t[0]
            result.append({"id":t[0],"time":t[1],"week":t[2]})
    return result
        
def countTime():#获取当天需要喂食的时间列
    print("countTime")
    list=getList()
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
                    DataClass.set_value("food_running_time",{"week":t["week"],"time":t["time"]})#记录当前正在喂食
                    print("下次喂食时间："+str(DataClass.get_value("food_run_time_list")))
                    next_time_flag=False
        
    if next_time_flag:
        DataClass.set_value("food_running_time","0")
    DataClass.set_value("food_run_time_list",rList)
        
def start():
    nowTime= datetime.date.today()
    nowHour=int(time.strftime("%H"))
    nowMinute=int(time.strftime("%M"))
    nextday=DataClass.get_value("next_time_date")#明天的日期
    differenceValue=(nextday-nowTime).days#明天的日期与今天的日期相减，判断当前的日期是否已经到了明天，值为0则表示到了第二天
    #print("当前时间:"+str(nowTime))
    #print("明天时间2:"+str(nextday))
    #print("时间差:"+str(differenceValue))
    if differenceValue==0:#当前日期已是第二天，明天日期需更新
        DataClass.set_value("next_time_date",datetime.datetime.now()+datetime.timedelta(days=1))
        countTime()#获取当天需要喂食的时间列
    list=DataClass.get_value("food_run_time_list")
    print(list)
    if len(list)>0:#当天有喂食时间
        for t in list:#循环遍历匹配当天需要喂食的时间
            tT=t["time"].split(":")
            tHour=int(tT[0])
            tMinute=int(tT[1])
            if tHour==nowHour and tMinute==nowMinute:
                list.remove(t)
                DataClass.set_value("food_run_time_list",list)
                print("*******************\n")
                print(DataClass.get_value("food_run_time_list"))
                food_run()
                break

    
