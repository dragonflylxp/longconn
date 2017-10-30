#coding=utf-8

import tornado.ioloop
import tornado.gen
import tornadoredis
from util.tools import Log
logger = Log().getLog()

#redis句柄
sub_hdr= None
blpop_hdr = None
TIMEOUT = 3

#注册消息处理回调
CHANNEL_TO_SUBSCRIBE = []
callbacks = {}
def subscribe_callback_register(channel):
    def decorator(func):
        if channel not in CHANNEL_TO_SUBSCRIBE:
            CHANNEL_TO_SUBSCRIBE.append(channel)
            callbacks[channel] = func
        else:
            logger.warning('[Channel:%s] already registered!',channel)
        return func
    return decorator

#初始化
config = {}
def set_up(confs):
    config.update(confs)

def attach(ioloop=None):
    global sub_hdr,blpop_hdr
    #消息队列客户端
    blpop_hdr = tornadoredis.Client(host=config["host"],
                                    port=config["port"],
                                    selected_db=config["db"],
                                    io_loop=ioloop)
    blpop_hdr.connect()
    #发布订阅客户端
    sub_hdr = tornadoredis.Client(host=config["host"],
                                  port=config["port"],
                                  selected_db=config["db"],
                                  io_loop=ioloop)
    sub_hdr.connect()
    sub_listen()

@tornado.gen.engine
def sub_listen():
    """订阅消息并监听
    """
    global sub_hdr
    yield tornado.gen.Task(sub_hdr.subscribe, CHANNEL_TO_SUBSCRIBE)
    sub_hdr.listen(sub_callback)

def sub_callback(msg):
    """订阅消息回调
       格式：Message(kind=u'message',
                     channel=u'channel#name',
                     body=u'bodystr',
                     pattern=u'channel#name')
    """
    if msg.kind != 'message':
        return

    try:
        callbacks[msg.channel](msg.channel,msg.body)
    except Exception as ex:
        logger.error(traceback.format_exc())

def blpop_callback(msg):
    """调用: blpop_hdr.blpop((key,), TIMEOUT, blpop_callback)
    """
    try:
        msg = msg.values()[0].encode('utf8')
        if msg:
            pass
    except Exception as ex:
        logger.error(ex)
