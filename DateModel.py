#!/usr/bin/python
# -*- coding:utf-8 -*-
#存储传感器状态
import mysql as Mysql
import OPi.GPIO as GPIO
import datetime
import socket
class DateModel(object):

    def __init__(self):
        self.ws=None
        self.webApp=None
        self.socketIO=None
        self.Temp=0#空气温度值
        self.Light = 0 ##光照值
        self.humidity=0#湿度值
        #turanshidu=0,#土壤湿度值
        self.watertemp = 0 #水温值

        self.version="2.0.0.0"#当前硬件代码版本
        self.productId= 0 #硬件产品ID
        self.ip=""#设备内网IP

        self.tempStatus = 0 #温度传感器状态
        self.lightStatus = 0 #光照传感器状态
        self.penshui_status=0 #喷雾控制器状态
        self.food_status=0  #喂食控制器状态值
        self.light_status=0 #电灯状态值
        self.humidity_status=0#湿度状态，0正常，1干旱
        self.watertemp_status=0#水温控制器
        self.webSocketStatus=0 #websocket状态
        self.isSend=False#手机端是否与设备建立连接状态码
        self.webLinkStatus=0 #内网连接状态
        self.webStatus=0 #内网服务启动状态

        self.autoClock=1 #自动控制状态值
        self.temp_auto=1#空气温度自动控制
        self.lamp_auto=1#电灯自动控制
        self.humidity_auto=1#湿度自动控制
        #turan_auto=1,#土壤湿度自动控制
        self.watertemp_auto=1#水温自动控制
        self.food_auto=1#喂食自动控制

        self.min_temp=0 #最低空气温度
        self.max_temp=0 #最高空气温度
        self.min_lamp=0 #最低光照
        self.max_lamp=0 #最高光照
        self.min_humidity=0 #最低湿度
        self.max_humidity=0 #最高湿度
        self.min_watertemp=0 #最低水温度
        self.max_watertemp=0 #最高水温度

        self.food_speed=0#0 慢，1快
        self.food_chixu_time=10#喂食启动后持续运转时间,单位：秒
        self.food_running_time=""#下次自动喂食的时间
        self.nowWeek=0#当前时间是星期几 0-6分别为日、一、二、三、四、五、六
        self.food_run_time_list=[]#当天将要运行喂食的时间段
        self.next_time_date=""#明天的日期


        self.watertemp_pin=19#水温加热控制器
        self.penshui_pin=12 #喷水控制器
        self.lamp_pin=8 #灯光控制器
        self.temp_pin=21 #空气加热控制器
        self.food_pin1=23#自动喂食接口1
        self.food_pin2=10#自动喂食接口2
        self.food_pin3=22#自动喂食接口3
        self.food_pin4=24#自动喂食接口4
        
    def dateInit(self):#传感器的设置数据初始化
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.penshui_pin, GPIO.OUT)
        GPIO.setup(self.lamp_pin, GPIO.OUT)
        GPIO.setup(self.watertemp_pin, GPIO.OUT)
        GPIO.setup(self.temp_pin, GPIO.OUT)
        GPIO.setup(self.food_pin1, GPIO.OUT)      # Set pin's mode is output
        GPIO.setup(self.food_pin2, GPIO.OUT)
        GPIO.setup(self.food_pin3, GPIO.OUT)
        GPIO.setup(self.food_pin4, GPIO.OUT)
        
        GPIO.output(self.penshui_pin, GPIO.LOW)
        GPIO.output(self.lamp_pin, GPIO.LOW)
        GPIO.output(self.watertemp_pin, GPIO.LOW)
        GPIO.output(self.temp_pin, GPIO.LOW)

        Mysql.setDb()
        productId=Mysql.select("select devicenum from info ")[0]
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
            self.food_auto=int(food_auto[1])
        else:
            print ("food_auto:***********")
            Mysql.insert("""insert into device values('food_auto','1','0','0')""")
            self.food_auto=1
        if(food_speed is not None):
            self.food_speed=int(food_speed[2])
        else:
            Mysql.insert("""insert into device values('food_speed','','0','0')""")
            self.food_speed=0
        if(food_chixu_time is not None):
            self.food_chixu_time=int(food_chixu_time[2])
        else:
            Mysql.insert("""insert into device values('food_chixu_time','','10','0')""")
            self.food_chixu_time=10
        self.productId=productId
        self.min_temp=int(TempList[2])
        self.max_temp=int(TempList[3])
        self.min_lamp=int(LightList[2])
        self.max_lamp=int(LightList[3])
        self.min_humidity=int(humidityList[2])
        self.max_humidity=int(humidityList[3])
        self.min_watertemp=int(watertempList[2])
        self.max_watertemp=int(watertempList[3])

        self.autoClock=int(autoClock[1])
        self.temp_auto=int(temp_auto[1])
        self.lamp_auto=int(lamp_auto[1])
        self.humidity_auto=int(humidity_auto[1])
        #self.turan_auto=int(turan_auto[1])
        self.watertemp_auto=int(watertemp_auto[1])
        
        self.setTomorrow()
        Mysql.closeDb()
    
    def getMapDate(self):
        msg={"msg":"get","list":{"light":str(self.Light),"temp":str(self.Temp),
"humidity":str(self.humidity),"watertemp":str(self.watertemp),
"critical":{"lamp":{"min":str(self.min_lamp),"max":str(self.max_lamp)},
"temp":{"min":str(self.min_temp),"max":str(self.max_temp)},
"humidity":{"min":str(self.min_humidity),"max":str(self.max_humidity)},
"watertemp":{"min":str(self.min_watertemp),"max":str(self.max_watertemp)},
"food":{"food_speed":self.food_speed,"food_running_time":self.food_running_time,"food_chixu_time":self.food_chixu_time}},
"status":{"lamp":str(self.light_status),"watertemp":str(self.watertemp_status),
"penshui":str(self.penshui_status),"temp":str(self.tempStatus)},
"auto":{"autoClock":str(self.autoClock),"temp_auto":str(self.temp_auto),"lamp_auto":str(self.lamp_auto),
"humidity_auto":str(self.humidity_auto),"watertemp_auto":str(self.watertemp_auto),"food_auto":str(self.food_auto)}}}
        return msg

    def getDateByName(self,name):#通过变量名来获取类中的变量值
        return getattr(self, name)
        
    def setValueByName(self,name,value):#通过变量名来修改变量值
        #print("name:"+name)
        #print("value:"+value)
        setattr(self, name, value)
        
    def open(self,type):#控制器打开
        #print str(type)
        GPIO.output(self.getDateByName(type), GPIO.HIGH)#高电平触发
        
    def close(self,type):#控制器关闭
        GPIO.output(self.getDateByName(type), GPIO.LOW)    
        
    def setDevice(self,obj):#修改设备的监控范围
        min=obj["min"]
        max=obj["max"]
        device=obj["device"]
        self.setValueByName("min_"+device,min)
        self.setValueByName("max_"+device,max)
        sql=str("update device set min_value="+min+",max_value="+max+" where name='"+device+"'")
        #print sql
        Mysql.setDb()
        Mysql.update(sql)
        Mysql.closeDb()
        
    def changeAuto(self,type,status):#改变设备的自动控制状态
        self.setValueByName(str(type),status)
        sql=str("update device set status="+status+" where name='"+type+"'")
        #print sql
        Mysql.setDb()
        Mysql.update(sql)
        Mysql.closeDb()
        
    def changeDevice(self,type,status,Food):#手动改变控制器状态
        #print str(type)
        if int(status)==0:
            #penshui.close(type)
            self.close(str(type))
            if type=='penshui_pin':
                self.penshui_status=0
            if type=='lamp_pin':
                self.light_status=0
            if type=='food_pin':
                self.food_status=0
            if type=='watertemp_pin':
                self.watertemp_status=0
            if type=='temp_pin':
                self.tempStatus=0
        if int(status)==1:
            if type=='food_pin':
                Food.food_run()
            else:
                self.open(str(type))
                if type=='penshui_pin':
                    self.penshui_status=1
                if type=='lamp_pin':
                    self.light_status=1
                if type=='food_pin':
                    self.food_status=1
                if type=='watertemp_pin':
                    self.watertemp_status=1
                if type=='temp_pin':
                    self.tempStatus=1

    #自动控制控制器状态
    def autoControl(self,Food):
        Temp=int(self.Temp)
        min_temp=int(self.min_temp)
        max_temp=int(self.max_temp)
        humidity=int(self.humidity)
        min_humidity=int(self.min_humidity)
        max_humidity=int(self.max_humidity)
        Light=int(self.Light)
        min_lamp=int(self.min_lamp)
        max_lamp=int(self.max_lamp)
        watertemp=self.watertemp
        min_watertemp=int(self.min_watertemp)
        max_watertemp=int(self.max_watertemp)
    ############################################
        if int(self.temp_auto)==1:#空气加温
            
            if Temp<min_temp:
                
                self.open("temp_pin")
                self.tempStatus=1
            else:
                self.close("temp_pin")
                self.tempStatus=0

    ############################################
        if int(self.lamp_auto)==1:#电灯
            if Light<min_lamp:
                self.open("lamp_pin")
                self.light_status=1
            else:
                self.close("lamp_pin")
                self.light_status=0

    #################################################
        if int(self.humidity_auto)==1:#湿度
            if humidity<min_humidity:
                self.open("penshui_pin")
                self.penshui_status=1
                self.humidity_status=1
            else:
                self.close("penshui_pin")
                self.penshui_status=0
                self.humidity_status=0

    #########################################
        if int(self.watertemp_auto)==1:#水湿度
            if watertemp<float('%.1f'%min_watertemp):
                self.open("watertemp_pin")
                self.watertemp_status=1
            else:
                self.close("watertemp_pin")
                self.watertemp_status=0

        if int(self.food_auto)==1:#湿度
            Food.start()
    
    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            self.ip = s.getsockname()[0]
        except Exception,e:
            self.ip = "0.0.0.0"
        finally:
            s.close()
    def setTomorrow(self):#设置明天的日期
        self.next_time_date=datetime.date.today()+datetime.timedelta(days=1)#明天的日期