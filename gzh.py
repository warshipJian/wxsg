#!/usr/bin/env python
# coding:utf8

import os, re, sys, time, errno,base64
import random
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
    f = tempfile.TemporaryFile()
    f.write(img)
    im = Image.open(f)
    img_name = str(time.time()) + '.jpg'
    print(img_name)
    im.save('/opt/code/' + img_name)
    return code

def identify_image_callback_showapi_sogou(img):
    # 搜狗验证码是6位
    code = getCode(img,'36')
    print('识别搜狗验证码: ' + code)
    return code

def identify_image_callback_showapi_weixin(img):
    # 微信验证码是4位
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

    #use_proxies = 2
    #ws_api = WechatSogouAPI()
    ws_api = WechatSogouAPI(proxies=proxies)
    while True:
        # 注意下磁盘空间，不够时停止爬取
        fdisk = tools.fdisk()
        if fdisk.status() == 2:
            print('磁盘空间不足')
            time.sleep(60*60*24*30) 

        gzh_name = r.lpop('gzh')
        if gzh_name:
            gzh_tmp = gzh_name.split('_')
            try:
                # 本地和代理轮着来
                #if use_proxies % 2 == 1:
                #    ws_api = WechatSogouAPI(captcha_break_time=1,proxies=proxies)
                #else:
                #    ws_api = WechatSogouAPI(captcha_break_time=1)
                data = ws_api.get_gzh_article_by_history(gzh_tmp[0],
                                                         identify_image_callback_sogou=identify_image_callback_showapi_sogou,
                                                         identify_image_callback_weixin=identify_image_callback_showapi_weixin)
            except exceptions.WechatSogouVcodeOcrException as e:
                #use_proxies += 1
                print(e)
                s = str(e)
                if '-6' in s:
                    print('代理有问题,睡一下再试')
                    # 代理或本地ip有问题时，睡眠11分钟后再试
                    time.sleep(60*41)
                else:
                    print('验证码或其他问题')
                continue

            # 处理爬取到的文章
            gzh = {}
            if 'article' not in data:
                print(data)
                continue
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
            # 防止被封ip
            time.sleep(random.randrange(1,10))
        else:
            print('取完了')
            time.sleep(300)
