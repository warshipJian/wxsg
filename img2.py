#!/usr/bin/env python
# coding:utf8

"""
验证码识别
"""

#encoding=utf-8
###利用点的密度计算
from PIL import Image,ImageEnhance,ImageFilter,ImageDraw
import sys
import pytesseract
#计算范围内点的个数
def numpoint(im):
    w,h = im.size
    data = list( im.getdata() )
    mumpoint=0
    for x in range(w):
        for y in range(h):
            if data[ y*w + x ] !=255:#255是白色
                mumpoint+=1
    return mumpoint

#计算5*5范围内点的密度
def pointmidu(im):
    im.save(r'img.jpg')
    w,h = im.size
    p=[]
    for y in range(0,h,5):
        for x in range(0,w,5):
            box = (x,y, x+5,y+5)
            im1=im.crop(box)
            a=numpoint(im1)
            if a<11:##如果5*5范围内小于11个点，那么将该部分全部换为白色。
                for i in range(x,x+5):
                    for j in range(y,y+5):
                        if i >= w:
                            continue
                        if j >= h:
                            continue
                        im.putpixel((i,j), 255)
    im.save(r'img.jpg')

def ocrend():##识别
    image_name = "img.jpg"
    im = Image.open(image_name)
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')
    im.save("1.tif")
    print(pytesseract.image_to_string('1.tif'))

if __name__=='__main__':
    image_name = "/tmp/code.png"
    im = Image.open(image_name)
    im = im.filter(ImageFilter.DETAIL)
    im = im.filter(ImageFilter.MedianFilter())

    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')
    print(im.size)
    ##a=remove_point(im)
    pointmidu(im)
    ocrend()
