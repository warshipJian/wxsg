#!/usr/bin/env python
# coding:utf8

"""
更新未爬取到的文章
"""

import os, re, sys, time, errno
import tools,run
from Model import article_content,article
import mysql



if __name__ == '__main__':
    # 初始化数据库连接
    session = mysql.connect()

    # 找出status为0的文章
    a_content = session.query(article_content).filter(article_content.status == '0').all()

    for i in a_content:
        a = session.query(article).filter(article.id == i.article_id).one()
        aq = a.__dict__
        ad = {}
        ad['id'] = aq['id']
        ad['wechat_name'] = aq['wechat_name']
        ad['title'] = aq['title']
        ad['url'] = aq['url']
        ad['main_img'] = aq['main_img']
        ad['time'] = aq['time']
        ad['type'] = aq['type']
        run.spider(ad['type']).work(ad)

    session.close()