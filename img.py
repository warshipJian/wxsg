#!/usr/bin/env python
# coding:utf8

"""
验证码识别
"""

import re,base64,sys,time
import ast
from PIL import Image
import cStringIO
import pytesseract
from ShowapiRequest import ShowapiRequest

def getImage():
    fileName = '/tmp/code.png'
    img = Image.open(fileName)
    # 打印当前图片的模式以及格式
    print('未转化前的: ', img.mode, img.format)
    # 使用系统默认工具打开图片
    # img.show()
    return img

'''
1) 将图片进行降噪处理, 通过二值化去掉后面的背景色并加深文字对比度
'''
def convert_Image(img, standard=127.5):
    '''
    【灰度转换】
    '''
    image = img.convert('L')

    '''
    【二值化】
    根据阈值 standard , 将所有像素都置为 0(黑色) 或 255(白色), 便于接下来的分割
    '''
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    return image

'''
使用 pytesseract 库来识别图片中的字符
'''
def change_Image_to_text(img):
    '''
    如果出现找不到训练库的位置, 需要我们手动自动
    语法: tessdata_dir_config = '--tessdata-dir "<replace_with_your_tessdata_dir_path>"'
    '''
    #testdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
    textCode = pytesseract.image_to_string(img, lang='eng')
    # 去掉非法字符，只保留字母数字
    textCode = re.sub("\W", "", textCode)
    return textCode

def main():
    img = convert_Image(getImage())
    print('result：', change_Image_to_text(img))


if __name__ == '__main__':
    im = Image.open('./code/1543842489.56.jpg')
    buffer = cStringIO.StringIO()
    im.save(buffer,format="JPEG")
    img_base64 = base64.b64encode(buffer.getvalue())
    r = ShowapiRequest("http://route.showapi.com/184-5", "82117", "6e9549ad376b4fc588f3ca9b052eed12")
    r.addBodyPara("img_base64",img_base64)
    r.addBodyPara("typeId", "34")
    r.addBodyPara("convert_to_jpg", "0")
    r.addBodyPara("needMorePrecise", "0")
    #r.addFilePara("img", './code/1543841163.18.jpg') #文件上传时设置
    res = r.post()
    result = ast.literal_eval(res.text)
    print(result['showapi_res_body']['Result'])