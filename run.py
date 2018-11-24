#!/usr/bin/env python
#coding:utf8

import os,time,errno
import requests
import redis
import shutil
import urlparse
from pprint import pprint
from wechatsogou import WechatSogouAPI, WechatSogouConst
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import Model


class spider(object):

    def __init__(self,a_type):
        self.m_type = 'WechatSogouConst.hot_index.'
        self.a_type = a_type

        # 创建数据库连接
        engine = create_engine('mysql://root:123456@localhost:3306/wxsg')
        DBSession = sessionmaker(bind=engine)
        self.session =  DBSession()

        # 创建redis连接
        self.r = redis.Redis(host='localhost', port=6379, db=0)

    def __del__(self):
        # 释放数据库连接
        self.session.close()

        # 释放redis连接
        del self.r

    def create_article(self,session, gzh, article, a_type):
        """
        存取文章
        :param session:
        :param gzh:
        :param article:
        :param a_type:
        :return:
        """
        # 插入文章
        new_article = Model.article(
            wechat_name=gzh['wechat_name'],
            headimage=gzh['headimage'],
            headimage_local=gzh['headimage_local'],
            abstract=article['abstract'],
            main_img=article['main_img'],
            main_img_local=article['main_img_local'],
            open_id=article['open_id'],
            time=article['time'],
            title=article['title'],
            url=article['url'],
            type=a_type,
        )
        session.add(new_article)
        session.commit()

        # 爬取正文
        res = requests.get(article['url'])
        res.encoding = 'utf-8'

        # 插入正文
        new_article_content = Model.article_content(
            article_id=new_article.id,
            content=res.text,
        )
        session.add(new_article_content)
        session.commit()

    def get_img_path(self,img_url):
        """
        提取url的host和后面的路径
        :param img_url:
        :return:
        """
        urlparse_img = urlparse.urlparse(img_url)
        path = urlparse_img.path
        path = '/'.join(path.split('/')[0:-1])

        return os.getcwd() + '/' + urlparse_img.netloc + path

    def save_img(self,img_url,img_name,img_path):
        """
        存取图片
        :param img_url:
        :param img_name:
        :return:
        """
        if not img_url or not img_name or not img_path:
            return None

        img_url = "http://" + img_url.split("//")[-1]

        # 获取图片
        r = requests.get(img_url, stream=True)
        if r.status_code == 200:
            if not os.path.exists(img_path):
                try:
                    os.makedirs(img_path)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(img_path):
                        pass
                    else:
                        raise
            img_file = img_path + '/' + img_name
            with open(img_file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    def run(self):
        # 取时间
        last_time = self.r.get(self.a_type)
        if not last_time:
            last_time = 0
        else:
            last_time = int(last_time)
        max_time = last_time

        # 创建搜狗爬虫
        ws_api = WechatSogouAPI()

        # 开始爬取
        gzh_articles = getattr(ws_api, 'get_gzh_article_by_hot')(eval(self.m_type + self.a_type))
        for i in gzh_articles:
            gzh = i['gzh']
            article = i['article']
            time_now = int(article['time'])

            if  time_now > last_time:
                # 图片处理
                # 公众号头像
                img_url_gzh = gzh['headimage']
                img_path_gzh = self.get_img_path(img_url_gzh)
                img_name_gzh = 'gzh' + str(article['time']) + '_' + str(int(time.time())) + '.jpg'
                self.save_img(img_url_gzh, img_name_gzh, img_path_gzh)
                gzh['headimage_local'] = img_path_gzh + '/' +  img_path_gzh # 存储路径到数据库
                # 文章图片
                img_url_a = article['main_img']
                img_path_a = self.get_img_path(img_url_a)
                img_name_a = 'a' + str(article['time']) + '_' + str(int(time.time())) + '.jpg'
                self.save_img(img_url_a, img_name_a, img_path_a)
                article['main_img_local'] = img_path_a + '/' +  img_name_a # 存储路径到数据库

                # 文章处理
                self.create_article(self.session, gzh, article, self.a_type)

                # 打印下
                print(str(article['time']) + ' ' + '爬取' + gzh['wechat_name'] + ' ' + article['title'])

            # 更新最后一次的爬取时间，避免重复爬取
            if time_now > max_time:
                max_time = time_now

        self.r.set(self.a_type, max_time)

if __name__ == '__main__':
    ''' 类型
    养生堂 health
    科技咖 technology
    财经迷 finance
    生活家 life
    育儿 mummy
    星座 constellation
    私房话 sifanghua
    八封精 gossip
    时尚圈 fashion
    '''

    wxs = {
        '私房话':'sifanghua',
        '八封精':'gossip',
        '时尚圈':'fashion',
    }

    for k in wxs:
        s = spider(wxs[k])
        s.run()