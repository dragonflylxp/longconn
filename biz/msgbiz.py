# encoding: utf-8
import time
import ujson
import xmsgbus
from objects import Message
from util import db_pool
from dispatcher import BizMsgDispatcher

from util.tools import Log
logger = Log().getLog()

@xmsgbus.subscribe_callback_register("BizMsgChannel001")
def biz_msg_channel(channel, msg):
    """业务层消息分发, 可根据渠道编号做到分服、分机房
       解析消息格式，交给对应业务的连接作转发
    """
    msg = ujson.loads(msg)
    logger.info("Subscriber message :%s", msg)
    getattr(BizMsgDispatcher(), msg.get('biz','default'), getattr(BizMsgDispatcher(), "default"))(msg)

@xmsgbus.subscribe_callback_register("WebsockMsgChannel001")
def websock_msg_channel(channel, msg):
    """连接层消息分发, 可根据渠道编号做到分服、分机房
       解析消息格式，做相关的业务处理并返回
    """
    msg = ujson.loads(msg)
    logger.info("Subscriber message :%s", msg)
    rds = db_pool.get_redis("main")
    rds.publish('BizMsgChannel001', ujson.dumps(msg))
