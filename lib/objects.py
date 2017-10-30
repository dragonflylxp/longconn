#coding=utf-8

import time

class Message(dict):
    """长连接通信消息类，是所有业务场景发送消息的基本类型
    """

    def __init__(self, biz, roomid, ctx, typ, frm, to):
        """
        :param biz: 业务类型
        :param roomid: 房间id
        :param ctx: 消息内容
        :param typ: 消息类型(text/json...)
        :param frm: 消息发送
        :param to : 消息接收
        :param time: 消息时间
        """
        self['biz'] = biz
        self['roomid'] = roomid
        self['ctx'] = ctx
        self['typ'] = typ
        self['frm'] = frm
        self['to']  = to
        self['time']= time.time()

    @property
    def ctx(self):
        if self['typ'] == 'text':
            return self['ctx']
        if self['typ'] == 'json':
            try:
                return ujson.loads(self['ctx'])
            except:
                return {}
        return None
