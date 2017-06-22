#coding=utf-8

import traceback
import ujson
from connections import ConnectManager
from objects import Message
from util import db_pool

class BaseDispatcher(object):
    pass

class WebSockMsgDispatcher(BaseDispatcher):
    """客户端消息处理
    """
    @classmethod
    def ping(cls, handler, msg):
        handler.write_message('pong')

    @classmethod
    def checkin(cls, handler, msg):
        """订阅，更新conn_pool
        """
        ConnectManager().register(handler, msg)

    @classmethod
    def checkout(cls, handler, msg):
        """取消订阅,更新conn_pool
        """
        ConnectManager().clear(handler, msg)

    @classmethod
    def biz(cls, handler, msg):
        """业务消息直接下发给业务层
             todo:
                1.通信方式: redis/zeromq/rabbitmq/grpc
                2.通信协议: json/protobuf
        """
        biz = msg.get('biz')
        roomid = msg.get('roomid')
        frm = msg.get('frm', 'sys')
        to  = msg.get('to', 'all')
        ctx = msg.get('ctx')
        typ = msg.get('typ','text')
        if biz in ['chat','vguess','versus']:
            message = Message(biz,ctx,typ,frm,to)
            rds = db_pool.get_redis("main")
            rds.publish('WebsockMsgChannel001', ujson.dumps(message))
        else:
            pass

    @classmethod
    def default(cls, handler, msg):
        pass

class BizMsgDispatcher(BaseDispatcher):
    """下层业务消息处理
    """
    @classmethod
    def chat(cls, msg):
        try:
            uid = msg.get('to')
            if uid == 'all':
                ConnectManager().send_all(msg)
            else:
                ConnectManager().send_to(uid, msg)
        except Exception as e:
            print traceback.format_exc()

    @classmethod
    def vguess(cls, msg):
        pass

    @classmethod
    def versus(cls, msg):
        pass

    @classmethod
    def default(cls, handler, msg):
        pass
