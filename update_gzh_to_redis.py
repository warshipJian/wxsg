#!/usr/bin/env python
# coding:utf8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from Model import article_content,article
import redis
import mysql

if __name__ == '__main__':
    session = mysql.connect()

    r = redis.Redis(host='localhost', port=6379, db=1)

    a_dis = session.execute('select wechat_name,type from article;')
    tmp = []
    for i in a_dis.fetchall():
        key = '_'.join(i)
        if key not in tmp:
            tmp.append(key)
            r.lpush('gzh',key)