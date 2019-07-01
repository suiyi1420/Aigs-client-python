# -*- coding:utf-8 -*-
from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont, ImageDraw


class LEDDrivers(object):
    def __init__(self,DateModel):
        self.DateModel=DateModel
        try:
            self.device = ssd1306(port=0, address=0x3C)  # rev.1 users set port=0
        except Exception,e:
            self.device =None
    def states(self,status):
        if str(status)=='1':
            return u"打开"
        else:
            return u"关闭"
    def setDraw(self):
        if self.device is not None:
            if str(self.DateModel.webSocketStatus)=='1':
                wsString=u'已连接'
            else:
                wsString=u'未连接'
            temp_statusString=self.states(self.DateModel.tempStatus)
            penshui_statusString=self.states(self.DateModel.penshui_status)
            watertemp_statusString=self.states(self.DateModel.watertemp_status)
            light_statusString=self.states(self.DateModel.light_status)
            tempString=str(int(self.DateModel.Temp))+u'℃'
            humidityString=(str(self.DateModel.humidity)+'%').decode("unicode_escape")
            watertempString=str(self.DateModel.watertemp)+u'℃'
            lampString=(str(self.DateModel.Light)+'lx').decode("unicode_escape")
            with canvas(self.device) as draw:
                #font2 = ImageFont.load_default()
                font = ImageFont.truetype("/root/demo/web/fonts/fzht.TTF", 13)
                font2 = ImageFont.truetype("/root/demo/web/fonts/fzht.TTF", 12)
                font3 = ImageFont.truetype("/root/demo/web/fonts/fzht.TTF", 10)
                font4 = ImageFont.truetype("/root/demo/web/fonts/fzht.TTF", 8)
                draw.text((0, 0), text=wsString, font=font3, fill=255)
                draw.text((35, 0), text="ip:"+self.DateModel.ip, font=font3, fill=255)
                draw.text((0, 6), text='--------------------------', font=font4, fill=255)
                draw.text((0, 13), text=u'气温:', font=font, fill=255)
                draw.text((30, 14), text=tempString, font=font2, fill=255)
                draw.text((65, 13), text=u'水温:', font=font, fill=255)
                draw.text((95, 14), text=watertempString, font=font2, fill=255)
                draw.text((0, 27), text=u'湿度:', font=font, fill=255)
                draw.text((30, 28), text=humidityString, font=font2, fill=255)
                draw.text((65, 27), text=u'亮度:', font=font, fill=255)
                draw.text((95, 28), text=lampString, font=font2, fill=255)
                draw.text((0, 37), text='--------------------------', font=font4, fill=255)
                draw.text((7, 43), text=u'加热灯:', font=font3, fill=255)
                draw.text((41, 43), text=temp_statusString, font=font3, fill=255)
                draw.text((67, 43), text=u'加湿器:', font=font3, fill=255)
                draw.text((101, 43), text=penshui_statusString, font=font3, fill=255)
                draw.text((7, 53), text=u'加热棒:', font=font3, fill=255)                    
                draw.text((41, 53), text=watertemp_statusString, font=font3, fill=255)
                draw.text((67, 53), text=u'电灯:', font=font3, fill=255)
                draw.text((101, 53), text=light_statusString, font=font3, fill=255)
