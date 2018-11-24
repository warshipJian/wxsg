#!/usr/bin/env python
#coding:utf8

'''
阿布云代理
'''

import requests

class abuyun:

    def __init__(self,url):
        self.url = url

    def html_requests(self):

        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息
        proxyUser = "H39457KL2A9S01HD"
        proxyPass = "FD281A5546AE2FCC"

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

        resp = requests.get(self.url, proxies=proxies)
        return resp