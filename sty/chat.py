#coding=utf-8
from base import BaseStrategy

"""聊天业务
    1.消息结构
    {
        'biz':'chat',         #业务类型
        'frm':'1134506',      #sender
        'to' :'all',          #receiver
        'type': 'text',       #消息格式: text/json/...
        'ctx':'hello world!'  #消息内容
    }

"""


class ChatStrategy(BaseStrategy):
    """聊天(弹幕)策略类
    """

    def __init__(self, sty_name='chat'):
        super(ChatStrategy, self).__init__(sty_name)

    def parse(self, msg):
        pass
