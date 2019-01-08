# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import json
import re

import requests
from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import XML

from wechatsogou.exceptions import WechatSogouException
from wechatsogou.five import str_to_bytes
from wechatsogou.tools import get_elem_text, list_or_empty, replace_html, get_first_of_element

backgroud_image_p = re.compile('background-image:[ ]+url\(\"([\w\W]+?)\"\)')
js_content = re.compile('js_content.*?>((\s|\S)+)</div>')
find_article_json_re = re.compile('var msgList = (.*?)}}]};')
get_post_view_perm = re.compile('<script>var account_anti_url = "(.*?)";</script>')


class WechatSogouStructuring(object):

    @staticmethod
    def get_article_detail(text, del_qqmusic=True, del_voice=True):
        """根据微信文章的临时链接获取明细

        1. 获取文本中所有的图片链接列表
        2. 获取微信文章的html内容页面(去除标题等信息)

        Parameters
        ----------
        text : str or unicode
            一篇微信文章的文本
        del_qqmusic: bool
            删除文章中的qq音乐
        del_voice: bool
            删除文章中的语音内容

        Returns
        -------
        dict
        {
            'content_html': str # 微信文本内容
            'content_img_list': list[img_url1, img_url2, ...] # 微信文本中图片列表

        }
        """
        # 1. 获取微信文本content
        html_obj = BeautifulSoup(text, "lxml")
        find_2 = False
        content_text = html_obj.find('div', {'class': 'rich_media_content', 'id': 'js_content'})

        if not content_text:
            content_text = html_obj.find('script', {'id': 'content_tpl', 'type': 'text/html'})
            html = str(content_text)
            find_2 = html.replace('<script id="content_tpl" type="text/html">','')
            find_2 = find_2.replace('</script>', '')

        if not content_text:
            return False

        # 2. 删除部分标签
        if del_qqmusic:
            qqmusic = content_text.find_all('qqmusic')
            for music in qqmusic:
                music.parent.decompose()

        if del_voice:
            # voice是一个p标签下的mpvoice标签以及class为'js_audio_frame db'的span构成，所以将父标签删除
            voices = content_text.find_all('mpvoice')
            for voice in voices:
                voice.parent.decompose()

        # 3. 获取所有的图片 [img标签，和style中的background-image]
        all_img_set = set()
        all_img_element = content_text.find_all('img')
        for ele in all_img_element:
            # 删除部分属性
            img_url = ele.attrs['data-src']
            del ele.attrs['data-src']

            if img_url.startswith('//'):
                img_url = 'http:{}'.format(img_url)

            ele.attrs['src'] = img_url

            if not img_url.startswith('http'):
                raise WechatSogouException('img_url [{}] 不合法'.format(img_url))
            all_img_set.add(img_url)

        backgroud_image = content_text.find_all(style=re.compile("background-image"))
        for ele in backgroud_image:
            # 删除部分属性
            if ele.attrs.get('data-src'):
                del ele.attrs['data-src']

            if ele.attrs.get('data-wxurl'):
                del ele.attrs['data-wxurl']
            img_url = re.findall(backgroud_image_p, str(ele))
            if not img_url:
                continue
            all_img_set.add(img_url[0])

        # 4. 处理iframe
        all_img_element = content_text.find_all('iframe')
        for ele in all_img_element:
            # 删除部分属性
            img_url = ele.attrs['data-src']
            del ele.attrs['data-src']
            ele.attrs['src'] = img_url

        # 5. 返回数据
        all_img_list = list(all_img_set)

        if find_2:
            content_html = find_2
        else:
            content_html = content_text.prettify()
            # 去除div[id=js_content]
            content_html = re.findall(js_content, content_html)[0][0]
        return {
            'content_html': content_html,
            'content_img_list': all_img_list
        }
