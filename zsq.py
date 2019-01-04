#!/usr/bin/env python
#coding:utf8

def log(f):
    '''
    def wrapper():
         print("before")
         f()
         print("after")

    return wrapper
    '''
    print("before")
    f()
    print("after")

@log
def greeting():
    print("Hello, World!")

greeting()