# -*- coding:utf-8 -*-
##内网和外网的通用接收信息方法
import zipfile
import urllib
import json
import os
import mysql as Mysql

def getFromWeb(self,message):
    obj = json.loads(message)
    type = obj['msg']
    if type == 'connect':#手机端与硬件建立连接后，手机端发送connect指令，则获取硬件当前的状态，若当前为手动控制，则获取硬件各传感器和控制器的状态，同时发送connect指令给手机端
        msg={"msg":'connect'}
        self.sendMessage(str(msg))
    if type == 'isSend':#手机端与硬件建立连接后，手机端发送connect指令，则获取硬件当前的状态，若当前为手动控制，则获取硬件各传感器和控制器的状态，同时发送connect指令给手机端
        issen=obj['isSend']
        if issen=="0":
            self.DateModel.isSend=False
        else:
            self.DateModel.isSend=True
    if type == 'change':#手机端与硬件建立连接后，手机端发送connect指令，则获取硬件当前的状态，若当前为手动控制，则获取硬件各传感器和控制器的状态，同时发送connect指令给手机端
        self.DateModel.autoClock=int(obj['value'])
        Mysql.setDb()
        Mysql.update(str("update device set status="+obj['value']+" where name='autoClock'"))
        Mysql.closeDb()   
    if type == 'set':#手机端发送change指令，则获取指令中的key值(需要改变的控制器)和对应的value值(改变的值是多少)，若为autoClock,则改变控制类型(自动、手动)。
        self.DateModel.setDevice(obj)
    if type == 'changeDevice':#手机端发送changeDevice指令，改变控制器的状态,status:0-->关闭，1-->打开
        typ=obj['type']
        stat=obj['status']
        self.DateModel.changeDevice(typ,stat,self.Food)
    if type == 'setWifi':#手机端发送setWifi指令，设置WIFI帐号密码
        ssid=obj['ssid']
        password=obj['password']
        cmd=["source /etc/network/interfaces.d/*\n","auto wlan0\n","allow-hotplug wlan0\n","iface wlan0 inet dhcp\n",'wpa-ssid "'+ssid+'"\n','wpa-psk "'+password+'"\n']
        f1 = open('/etc/network/interfaces', 'w')
        f1.writelines(cmd)
        f1.close()
        os.system("reboot")
    if type == 'changeAuto':#手机端发送changeAuto指令，改变自动控制的各个传感器的自动控制状态
        typ=obj['type']
        stat=obj['status']
        #print(changeAuto)
        self.DateModel.changeAuto(typ,stat)
    if type == 'resetCamera':#手机端发送changeAuto指令，改变自动控制的各个传感器的自动控制状态
        os.system("systemctl restart camera")
    if type == 'addFoodTime':#手机端发送addFoodTime指令，添加自动喂食时间
        ftimeList=obj['list']
        self.Food.addTime(ftimeList)
    if type == 'setFoodSpeed':#手机端发送setFoodSpeed指令，设置自动喂食持续时间和速度
        ffood_speed=int(obj['food_speed'])
        ffood_chixu_time=int(obj['food_chixu_time'])
        #print("ffood_chixu_time:"+str(ffood_chixu_time))
        self.Food.setSpeed(ffood_speed,ffood_chixu_time)
    if type == 'deleteFoodTime':#手机端发送deleteFoodTime指令，删除自动喂食时间
        deleteId=obj['id']
        self.Food.deleteTime(deleteId)
    if type == 'food_time_list':#手机端发送获取喂食时间列表指令
        msg={"msg":'food_time_list',"list":self.Food.getList()}
        self.sendMessage(str(msg))
    if type == 'sysTime':#服务端发送更新系统时间指令
        sysTime=obj['sysTime']
        print("服务器时间："+str(sysTime))
        os.system('date -s "'+sysTime+'"')
        self.DateModel.setTomorrow()
    if type == 'update':#手机端发送update指令，检查硬件代码与云端的版本号是否一致，不一致则下载云端的最新代码，并提示重启应用
        version_could=obj['version']
        print("云端版本："+str(version_could))
        def Schedule(a,b,c):
            per = 100.0 * a * b / c
            print '%.2f%%' % per
        if self.DateModel.version!=version_could:
            url = 'http://www.fallwings.top/aigs/file/demo.zip'
            local = os.path.join('/root/','demo.zip')
            urllib.urlretrieve(url,local,Schedule)
            if ws is not None:
                msg={"msg":'update'}
                print str(msg)
                self.sendMessage(str(msg))
            azip = zipfile.ZipFile('/root/demo.zip')
            azip.extractall("/root/demo/")
            os.system("reboot")  