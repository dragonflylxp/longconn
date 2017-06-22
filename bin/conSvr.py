#coding=utf-8

import os
import argparse
import path
import xtornado
import websock
import xmsgbus
from util.configer import *
from util import db_pool
from util.tools import Log

def init(conf_file):
    # 载入配置文件
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    confs = JsonConfiger.get_instance()
    confs.load_file(conf_file)

    # 初始化日志
    log_cnf = confs.get('logging')
    if log_cnf['config_file'][:1] not in ['/', '\\']:
        log_cnf['config_file'] = os.path.join(os.path.dirname(os.path.abspath(conf_file)), log_cnf['config_file'])
    Log.set_up(log_cnf)
    global logger
    logger = Log().getLog()

    #加载业务代码
    xtornado.load_biz_dir(path._BIZ_PATH)

    xmsgbus.set_up(confs.get("database/redis/msgbus"))
    db_pool.set_up(confs.get("database"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Cmd options:')
    parser.add_argument('-c', default=os.path.join(path._ETC_PATH, 'includes_dev.json'), help="-c cfgfile ******加载配置文件")
    parser.add_argument('-p', type=int, default=8881, help="-p port ******启动端口")
    args = parser.parse_args();
    init(args.c)
    xtornado.listen(args.p)
    xmsgbus.attach()
    xtornado.start()
