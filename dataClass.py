#!/usr/bin/python
# -*- coding:utf-8 -*-
#存储传感器状态
import mysql as Mysql
import multiprocessing
def _init():
    global _global_data
    _global_data = {
"ws":None,
"socketIO":None,
"Temp" : 0 ,#空气温度值
"Light" : 0 ,##光照值
"humidity":0,#湿度值
#"turanshidu":0,#土壤湿度值
"watertemp" : 0 ,#水温值

"productId": "0", #硬件产品ID
"ws":None, #websocket

"tempStatus" : 0, #温度传感器状态
"lightStatus" : 0, #光照传感器状态
"penshui_status":0 ,#喷雾控制器状态
"food_status":0,  #喂食控制器状态值
"light_status":0 ,#电灯状态值
"humidity_status":0,#湿度状态，0正常，1干旱
"watertemp_status":0,#水温控制器
"webSocketStatus":0, #websocket状态

"autoClock":1, #自动控制状态值
"temp_auto":1,#空气温度自动控制
"lamp_auto":1,#电灯自动控制
"humidity_auto":1,#湿度自动控制
#"turan_auto":1,#土壤湿度自动控制
"watertemp_auto":1,#水温自动控制
"food_auto":1,#喂食自动控制

"min_temp":0, #最低空气温度
"max_temp":0, #最高空气温度
"min_lamp":0, #最低光照
"max_lamp":0, #最高光照
"min_humidity":0, #最低湿度
"max_humidity":0, #最高湿度
"min_watertemp":0, #最低水温度
"max_watertemp":0, #最高水温度

"food_speed":0,#0 慢，1快
"food_chixu_time":10,#喂食启动后持续运转时间,单位：秒
"food_running_time":"",#下次自动喂食的时间
"nowWeek":0,#当前时间是星期几 0-6分别为日、一、二、三、四、五、六
"food_run_time_list":[],#当天将要运行喂食的时间段
"next_time_date":"",#明天的日期


"watertemp_pin":19,#水温加热控制器
"penshui_pin":12, #喷水控制器
"lamp_pin":8, #灯光控制器
"food_pin":15, #喂食控制器
"temp_pin":21, #空气加热控制器
"food_pin1":23,#自动喂食接口1
"food_pin2":10,#自动喂食接口2
"food_pin3":22,#自动喂食接口3
"food_pin4":24,#自动喂食接口4

    }
    
    Mysql.setDb()
    
    TempList=Mysql.select("select * from device where name = 'temp' ")
    LightList=Mysql.select("select * from device where name = 'lamp' ")
    humidityList=Mysql.select("select * from device where name = 'humidity' ")
    watertempList=Mysql.select("select * from device where name = 'watertemp' ")

    autoClock=Mysql.select("select * from device where name = 'autoClock' ")
    temp_auto=Mysql.select("select * from device where name = 'temp_auto' ")
    lamp_auto=Mysql.select("select * from device where name = 'lamp_auto' ")
    humidity_auto=Mysql.select("select * from device where name = 'humidity_auto' ")
    #turan_auto=Mysql.select("select * from device where name = 'turan_auto' ")
    watertemp_auto=Mysql.select("select * from device where name = 'watertemp_auto' ")
    food_auto=Mysql.select("select * from device where name = 'food_auto' ")
    food_speed=Mysql.select("select * from device where name = 'food_speed' ")
    food_chixu_time=Mysql.select("select * from device where name = 'food_chixu_time' ")
    if(food_auto is not None):
        print ("food_auto:#######################")
        set_value("food_auto",int(food_auto[1]))
    else:
        print ("food_auto:***********")
        Mysql.insert("""insert into device values('food_auto','1','0','0')""")
        set_value("food_auto",1)
    if(food_speed is not None):
        set_value("food_speed",int(food_speed[2]))
    else:
        Mysql.insert("""insert into device values('food_speed','','0','0')""")
        set_value("food_speed",0)
    if(food_chixu_time is not None):
        set_value("food_chixu_time",int(food_chixu_time[2]))
    else:
        Mysql.insert("""insert into device values('food_chixu_time','','10','0')""")
        set_value("food_chixu_time",10)

    set_value("min_temp",int(TempList[2]))
    set_value("max_temp",int(TempList[3]))
    set_value("min_lamp",int(LightList[2]))
    set_value("max_lamp",int(LightList[3]))
    set_value("min_humidity",int(humidityList[2]))
    set_value("max_humidity",int(humidityList[3]))
    set_value("min_watertemp",int(watertempList[2]))
    set_value("max_watertemp",int(watertempList[3]))

    set_value("autoClock",int(autoClock[1]))
    set_value("temp_auto",int(temp_auto[1]))
    set_value("lamp_auto",int(lamp_auto[1]))
    set_value("humidity_auto",int(humidity_auto[1]))
    #set_value("turan_auto",int(turan_auto[1]))
    set_value("watertemp_auto",int(watertemp_auto[1]))
    
    Mysql.closeDb()
    

def set_value(name, value):
    _global_data[name] = value

def get_value(name, defValue=None):
    try:
        return _global_data[name]
    except KeyError:
        return defValue 

