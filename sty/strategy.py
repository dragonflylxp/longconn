#coding=utf-8
from connections import *

class Strategy_default(object):
    """策略类：根据业务场景聚合连接,分配房间号
    """
    @classmethod
    def alloc(cls, params):
        """分配房间, 业务场景重载此接口
        """
        raise NotImplementedError()

    @classmethod
    def dealloc(cls, params):
        """释放房间, 业务场景重载此接口
        """
        raise NotImplementedError()


class Strategy_chat(Strategy_default):
    """聊天场景
    """
    @classmethod
    def alloc(cls, params):
        return params.get('roomid', None)

    @classmethod
    def dealloc(cls, params):
        pass


class Strategy_vguess(object):
    """虚拟杯赛: 坐满优先
        从分布式共享缓存(redis)获取当前房间分布
        选择一个未坐满，且人数最多的房间号
    """
    @classmethod
    def alloc(cls, params):
        pass

    @classmethod
    def dealloc(cls, params):
        pass


class Strategy_versus(object):
    """对赌PK: 实力值匹配
    """
    @classmethod
    def alloc(cls, params):
        pass

    @classmethod
    def dealloc(cls, params):
        pass
