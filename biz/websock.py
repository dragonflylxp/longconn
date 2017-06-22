#coding=utf-8

import traceback
import ujson
from tornado.websocket import WebSocketHandler
import xtornado
from connections import ConnectManager
from dispatcher import WebSockMsgDispatcher
from util.tools import Log
logger = Log().getLog()

@xtornado.route_handler_class('/ws')
class MyWebsockHandler(WebSocketHandler):
    def prepare(self):
        pass

    def check_origin(self, origin):
        return True

    def open(self):
        args = {k:v[0] for k,v in self.request.arguments.items() if v}
        logger.info("[WEBSOCK:OPEN] args=%s|connid=%s", args, id(self))
        ConnectManager().create(self, args)

    def on_message(self, msg):
        """客户端websocket消息
            {
                'biz': 'chat/vguess/versus',
                'action': 'ping/checkin/checkout/biz',
                'roomid': '001',
                'uid': '123456',
                'frm': '123456',
                'to': 'all',
                'typ': 'json',
                'ctx': 'xxxxxx'
            }
        """
        try:
            msg = ujson.loads(msg)
            logger.debug("[WEBSOCK:RCVDMSG] receive message=%s",msg)
            action = msg.get("action")
            getattr(WebSockMsgDispatcher(), action, getattr(WebSockMsgDispatcher(), "default"))(self, msg)
            ConnectManager().refresh(self, msg)
        except Exception as e:
            print traceback.format_exc()

    def on_close(self):
        logger.info("[WEBSOCK:CLOSE] connid=%s", id(self))
        ConnectManager().remove(self)

    def write_message(self, msg):
        if not self.stream.closed():
            super(MyWebsockHandler,self).write_message(msg)
        else:
            self.on_connection_close()
