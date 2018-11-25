#!/usr/bin/env python
#coding:utf8

'''
阿布云代理
'''

import requests

class abuyun:

    def __init__(self,url):
        self.url = url

    def get_html(self):

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

        try:
            resp = requests.get(self.url, proxies=proxies)
            resp.encoding = 'utf-8'
            html = resp.text
        except:
            html = 'None'
        return html