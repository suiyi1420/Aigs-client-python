# -*- coding:utf-8 -*-
import eventlet
import socketio
import threading
import commonFun
eventlet.monkey_patch()#很重要，线程调度。不然无法使用，详情https://github.com/miguelgrinberg/python-socketio/issues/49

class Web(socketio.Namespace,threading.Thread):

    def __init__(self,nameSpace,DateModel,Food):
        #self=web
        super(Web, self).__init__(nameSpace)
        threading.Thread.__init__(self)
        self.DateModel=DateModel
        self.Food=Food
        self.sio = socketio.Server(logger=False)
        self.app = socketio.WSGIApp(self.sio, static_files={
                '/': '/root/demo/web/index.html',
                '/css':'/root/demo/web/css',
                '/js':'/root/demo/web/js',
                '/images':'/root/demo/web/images',
                '/fonts':'/root/demo/web/fonts',
            })

    def on_connect(self, sid, environ):#连接建立事件
        self.DateModel.webLinkStatus=1
        self.DateModel.webApp=self.sio
        

    def on_disconnect(self, sid):#连接关闭事件
        self.DateModel.webLinkStatus=0

    def on_response(self, sid, data):#收到消息事件
        print('response:'+str(data))
        commonFun.getFromWeb(self,data)
        
    def sendMessage(self,message):#信息发送函数
        self.sio.emit('response', message)

    def run(self):
        self.sio.register_namespace(self)
        self.DateModel.webApp=self.sio
        eventlet.wsgi.server(eventlet.listen(('', 80)),self.app,log_output=False)


    