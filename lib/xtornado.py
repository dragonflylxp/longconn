#coding=utf-8

import os
import imp
import tornado.web
import tornado.ioloop

#全局web对象
app = tornado.web.Application()

def get_app():
    return app

def add_handler(*args):
    app.add_handlers('.*$', [args])

def listen(port,address=''):
    return app.listen(port, address)

def start():
    tornado.ioloop.IOLoop.current().start()

def stop():
    tornado.ioloop.IOLoop.current().stop()

def current_ioloop():
    return tornado.ioloop.IOLoop.instance()

def route_handler_class(route_path, **kwargs):
    def deco_func(clazz):
        add_handler(route_path, clazz, kwargs)
        return clazz
    return deco_func

def load_biz_dir(dir_path):
    for fname in os.listdir(dir_path):
        if fname[-3:] != '.py':
            continue
        fpath = os.path.join(dir_path, fname)
        if not os.path.isfile(fpath):
            continue
        imp.load_source('_biz_' + fname[:-3], fpath)
