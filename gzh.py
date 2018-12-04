#!/usr/bin/env python
# coding:utf8

import os, re, sys, time, errno,base64
import requests
import redis
import shutil
import urlparse
import ast
from PIL import Image
from bs4 import BeautifulSoup
from wechatsogou import WechatSogouAPI, WechatSogouConst,exceptions
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import Model,run,tools
from ShowapiRequest import ShowapiRequest
import tempfile
import cStringIO

def getCode(img,typeId):
    '''
    :param img:
    :param typeId:
    :return:
    '''
    '''
    f = tempfile.TemporaryFile()
    f.write(img)
    im = Image.open(f)
    buffer = cStringIO.StringIO()
    im.save(buffer, format="JPEG")
    img_base64 = base64.b64encode(buffer.getvalue())
    '''
    img_base64 = base64.b64encode(img)
    r = ShowapiRequest("http://route.showapi.com/184-5", "82117", "6e9549ad376b4fc588f3ca9b052eed12")
    r.addBodyPara("img_base64", img_base64)
    r.addBodyPara("typeId", typeId)
    r.addBodyPara("convert_to_jpg", "0")
    r.addBodyPara("needMorePrecise", "0")
    res = r.post()
    result = ast.literal_eval(res.text)
    code = 'error_aaaa'
    if 'showapi_res_body' in result:
        if 'Result' in result['showapi_res_body']:
            code = result['showapi_res_body']['Result']
    return code

def identify_image_callback_showapi_sogou(img):
    code = getCode(img,'36')
    print('识别搜狗验证码: ' + code)
    return code

def identify_image_callback_showapi_weixin(img):
    code = getCode(img,'34')
    print('识别微信验证码: ' + code)
    return code

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

    use_proxies = 2
    while True:
        gzh_name = r.lpop('gzh')
        if gzh_name:
            gzh_tmp = gzh_name.split('_')
            try:
                if use_proxies % 2 == 1:
                    ws_api = WechatSogouAPI(captcha_break_time=1,proxies=proxies)
                else:
                    ws_api = WechatSogouAPI(captcha_break_time=1)
                data = ws_api.get_gzh_article_by_history(gzh_tmp[0],
                                                         identify_image_callback_sogou=identify_image_callback_showapi_sogou,
                                                         identify_image_callback_weixin=identify_image_callback_showapi_weixin)
            except exceptions.WechatSogouVcodeOcrException as e:
                use_proxies += 1
                print('验证码错误')
                sys.exit(0)

            gzh = {}
            if 'gzh' in data:
                gzh['wechat_name'] = data['gzh']['wechat_name']
                gzh['headimage'] = data['gzh']['headimage']
            else:
                gzh['wechat_name'] = gzh_name
                gzh['headimage'] = 'http://img1.cache.netease.com/catchpic/4/45/459BC016DCB46B2AD648E0D37D503E3A.jpg'
            for i in data['article']:
                article = {}
                article['abstract'] = i['abstract']
                article['main_img'] = i['cover']
                article['open_id'] = 0
                article['time'] = i['datetime']
                article['title'] = i['title']
                article['url'] = i['content_url']
                run.spider(gzh_tmp[1]).work(gzh, article)
        else:
            print('取完了')
            time.sleep(300)