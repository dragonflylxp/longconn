#coding=utf-8

import ujson
import time
import tornado
import strategy

CONN_TYPE_DFT  = 0X0000
CONN_TYPE_CHAT = 0x0001
CONN_TYPE_VGES = 0x0002
CONN_TYPE_vERS = 0x0004
CONN_TYPE_MATC = 0x0008
conn_type_map = {
    'default': CONN_TYPE_DFT,
    'chat':   CONN_TYPE_CHAT,
    'vguess': CONN_TYPE_VGES,
    'versus': CONN_TYPE_vERS,
    'matchlive': CONN_TYPE_MATC
}

CALLBACK_PERIOD = 20

#全局连接池:一个连接可复用多个长连接业务
conn_pool = {}

class ConnectObj(dict):
    """长连接对象
        标记业务类型和建连时间
    """
    def __init__(self, handler, uid, conn_type=CONN_TYPE_DFT):
        self['handler'] = handler
        self['uid']     = uid
        self['roomid']  = None
        self['conn_type'] = conn_type
        self['refresh'] = time.time()

    def __getitem__(self, key):
        try:
            return super(ConnectObj, self).__getitem__(key)
        except:
            return None

    def send(self, msg):
        self['handler'].write_message(msg)

    def is_biz(self, biz):
        return self['conn_type'] & biz

class ConnectManager(object):
    """连接管理类
       1.维护连接池, 添加和删除连接
       2.定时扫描连接池，剔除超时连接
    """
    @classmethod
    def create(cls, handler, params):
        uid = int(params.get('uid', 0))
        if not uid:
            return

        if not conn_pool.has_key(uid):
            conn_pool[uid] = ConnectObj(handler, uid)

    @classmethod
    def register(cls, handler, params):
        uid = int(params.get('uid', 0))
        if not uid:
            return

        if not conn_pool.has_key(uid):
            return

        #不同业务类型复用连接
        biz = params.get('biz','default')
        conn_type = conn_type_map.get(biz, CONN_TYPE_DFT)
        conn_type = conn_type | conn_pool[uid].get('conn_type')
        conn_pool[uid].update({'conn_type': conn_type})

        #登记房间号
        clazz = getattr(strategy, 'Strategy_'+biz)
        roomid = getattr(clazz, 'alloc')(params)
        conn_pool[uid].update({'roomid': roomid})

    @classmethod
    def clear(cls, handler, params):
        uid = int(params.get('uid', 0))
        if not uid:
            return

        if not conn_pool.has_key(uid):
            return

        #清除连接的某种业务类型
        biz = params.get('biz','default')
        conn_type = conn_type_map.get(biz, CONN_TYPE_DFT)
        conn_type = conn_pool[uid].get('conn_type') ^ conn_type
        conn_pool[uid].update({'conn_type': conn_type})

        #注销房间号
        clazz = getattr(strategy, 'Strategy_'+biz)
        getattr(clazz, 'dealloc')(params)
        conn_pool[uid].update({'roomid': None})

    @classmethod
    def remove(cls, handler):
        for uid, conn in conn_pool.iteritems():
            if id(handler) == id(conn['handler']):
                conn_pool.pop(uid)
                handler.close()

    @classmethod
    def refresh(cls, handler, params):
        uid = int(params.get('uid', 0))
        if not uid:
            return

        if conn_pool.has_key(uid):
            conn_pool[uid].update({'refresh':time.time()})

    @classmethod
    def send_to(cls, uid, msg):
        biz = conn_type_map.get(msg.get('biz','default'), CONN_TYPE_DFT)
        roomid = msg.get('roomid', None)
        msg = ujson.dumps(msg)
        conn = conn_pool.get(uid, None)
        if not conn or not conn.is_biz(biz):
            return
        if not roomid or roomid != conn['roomid']
            return
        conn.send(msg)

    @classmethod
    def send_all(cls, msg):
        for uid, conn in conn_pool.iteritems():
            ConnectManager.send_to(uid, msg)

    @classmethod
    def expire(cls):
        """清理超时连接
        """
        uids = conn_pool.keys()
        for uid in uids:
            conn = conn_pool.get(uid)
            if time.time()-conn['refresh'] > CALLBACK_PERIOD:
                conn_pool.pop(uid)
                handler.close()

    @classmethod
    def status(cls, biz=None, roomid=None):
        uids = []
        for uid , conn in conn_pool.iteritems():
            if biz and not conn.is_biz(biz):
                continue
            if roomid and conn['roomid'] != roomid:
                continue
            uids.append(uid)
        return uids

#周期性清理超时连接
tornado.ioloop.PeriodicCallback(ConnectManager.expire(), CALLBACK_PERIOD*1000).start()
