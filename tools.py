#!/usr/bin/env python
#coding:utf8

'''
基础工具
'''

import hashlib


class md5:

    def __init__(self,value):
        self.value = value

    def get_value(self):
        m = hashlib.md5()
        m.update(self.value)
        return m.hexdigest()