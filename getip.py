#!/usr/bin/env python
# coding:utf8

"""
获取代理ip
"""

import requests
import redis


def getip():
    r = redis.Redis(host='localhost', port=6379, db=1)
    url = 'https://proxyapi.mimvp.com/api/fetchsecret.php?orderid=863080108561521806&num=100&http_type=3&result_fields=1,2,3'
    req = requests.get(url)
    if req.ok:
        html = req.text
        for proxy in html.split('\n'):
            if 'HTTP/HTTPS' in proxy:
                val = proxy.split(',')
                ip = val[0]
                print(ip)
                r.lpush('proxy', ip)

if __name__ == '__main__':
    getip()