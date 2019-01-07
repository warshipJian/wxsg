#!/usr/bin/env python
# coding:utf8

import config
from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker

def connect():
    # 创建数据库连接
    db_conf = config.database()
    engine = create_engine('mysql://%s:%s@localhost:3306/%s?charset=utf8mb4' %
                           (db_conf['user'], db_conf['password'], db_conf['database']),
                           pool_pre_ping=True)
    DBSession = sessionmaker(bind=engine)
    return DBSession()