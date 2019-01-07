#!/usr/bin/env python
#coding:utf8

'''
阿布云代理
'''

import requests
import config

class abuyun:

    def __init__(self,url):
        self.url = url

    def get_html(self):

        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息
        conf = config.abuyun()
        proxyUser = conf['proxyUser']
        proxyPass = conf['proxyPass']

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

        headers = {'Connection': 'close'}

        try:
            resp = requests.get(self.url, proxies=proxies, headers=headers)
            resp.encoding = 'utf-8'
            html = resp.text
        except:
            html = 'None'
        return html