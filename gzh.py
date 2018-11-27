#!/usr/bin/env python
# coding:utf8

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
import Model,run,tools


def unlock_callback_example():
    return False

if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=1)
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H18ZRW855Y92O12D"
    proxyPass = "254043017FECCFAE"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    ws_api = WechatSogouAPI(captcha_break_time=3)
    while True:
        gzh_name = r.lpop('gzh')
        if gzh_name:
            gzh_tmp = gzh_name.split('_')
            data = ws_api.get_gzh_article_by_history(gzh_tmp[0],None,unlock_callback_sogou=unlock_callback_example)
            gzh_data = data['gzh']
            for i in data['article']:
                gzh = {}
                article = {}
                gzh['wechat_name'] = gzh_data['wechat_name']
                gzh['headimage'] = gzh_data['headimage']
                article['abstract'] = i['abstract']
                article['main_img'] = i['cover']
                article['open_id'] = 0
                article['time'] = i['datetime']
                article['title'] = i['title']
                article['url'] = i['content_url']
                run.spider(gzh_tmp[1]).work(gzh, article)
            #print(data)
                #run.spider('').work(data['gzh'],data[''])
        else:
            print('取完了')
            time.sleep(300)