#!/usr/bin/env python
# coding:utf8

"""
更新那些失败的文章
"""

import os, re, sys, time, errno
import requests
import redis
import shutil
import urlparse
from bs4 import BeautifulSoup
from wechatsogou import WechatSogouAPI, WechatSogouConst
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update
from abuyun import abuyun
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

        if not a:
            continue

        # 爬取正文
        html = abuyun(a.url).get_html()

        # 更新正文和图片
        if '<!DOCTYPE html>' in html:
            i.content = html
            i.status = 1
            session.commit()

            # 分析正文内容，提取图片
            soup = BeautifulSoup(html, "html.parser")
            images = soup.find_all('img')
            if images:
                a_id = a.id
                for image in images:
                    data_src = image.get('data-src')
                    if data_src:
                        img_path = run.spider('',1).save_img(data_src)
                        if img_path:
                            run.spider('', 1).create_article_img(session, a_id, img_path, data_src)
                    src = image.get('src')
                    if src:
                        img_path = run.spider('',1).save_img(src)
                        if img_path:
                            run.spider('', 1).create_article_img(session, a_id, img_path, src)

    session.close()