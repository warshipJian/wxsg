#!/usr/bin/env python
# coding:utf8

import os, re, sys, time, errno
import requests
import redis
import shutil
import urlparse
from bs4 import BeautifulSoup
from wechatsogou import WechatSogouAPI, WechatSogouConst
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import Model
from abuyun import abuyun
import tools


class spider(object):

    def __init__(self, a_type, page=10, check_time=True):
        self.m_type = 'WechatSogouConst.hot_index.'
        self.a_type = a_type
        self.page = page
        self.check_time = check_time

        # 创建数据库连接
        engine = create_engine('mysql://root:123456@localhost:3306/wx?charset=utf8mb4', pool_pre_ping=True)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

        # 创建redis连接
        self.r = redis.Redis(host='localhost', port=6379, db=1)

    def __del__(self):
        # 释放数据库连接
        self.session.close()

        # 释放redis连接
        del self.r

    def create_article(self, session, gzh, article, a_type):
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
        return new_article.id

    def create_article_content(self, session, html, article_id,status):
        """
        存取正文
        :param session:
        :param html:
        :param article_id:
        :param status:
        :return:
        """
        # 插入正文
        new_article_content = Model.article_content(
            article_id=article_id,
            content=html,
            status=status,
        )
        session.add(new_article_content)
        session.commit()
        return new_article_content.id

    def create_article_img(self, session, article_id, img_path, url):
        """
        存取图片
        :param session:
        :param id:
        :param img_path:
        :param url:
        :return:
        """
        # 插入图片
        new_article_img = Model.article_img(
            article_id=article_id,
            local=img_path,
            url=url,
        )
        session.add(new_article_img)
        session.commit()
        return new_article_img.id

    def get_img_path(self, img_url):
        """
        根据url，提取地址和图片名
        :param img_url:
        :return:
        """
        urlparse_img = urlparse.urlparse(img_url)
        path = urlparse_img.path
        path_tmp = path.split('/')
        path = '/'.join(path_tmp[0:-1])
        name = path_tmp[-1]
        if urlparse_img.query:
            name_tmp = tools.md5(urlparse_img.query).get_value()
            name = self.a_type + '_' + name_tmp + '.jpg'
        else:
            pattern = re.compile(r'(.*)?jpg')
            match = pattern.match(name)
            if not match:
                name = name + '.jpg'

        return '/opt/img/' + time.strftime("%Y/%m/%d/", time.localtime()) + urlparse_img.netloc + path, name

    def save_img(self, img_url):
        """
        存取图片
        :param img_url:
        :param img_name:
        :return:
        """
        img_path, img_name = self.get_img_path(img_url)
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
                return img_file
        else:
            return False

    def work(self, gzh, article):
        # 去掉重复的文章，即同一个公众号，同一时间内的同一个标题的文章
        a_dis = self.session.query(Model.article)\
            .filter(Model.article.title == article['title'])\
            .filter(Model.article.time == article['time'])\
            .filter(Model.article.wechat_name == gzh['wechat_name'])\
            .first()
        if a_dis:
            return 'yes'

        # 公众号头像处理
        gzh['headimage_local'] = 'None'
        img_file_gzh = self.save_img(gzh['headimage'])  # 传url，图片名称，图片地址
        if img_file_gzh:
            gzh['headimage_local'] = img_file_gzh  # 存储路径到数据库

        # 文章首图片处理
        article['main_img_local'] = 'None'
        img_file_a = self.save_img(article['main_img'])  # 传url，图片名称，图片地址
        if img_file_a:
            article['main_img_local'] = img_file_a  # 存储路径到数据库

        # 文章处理
        a_id = self.create_article(self.session, gzh, article, self.a_type)

        # 爬取正文
        html = abuyun(article['url']).get_html()

        # 存储正文
        status = 1
        if '<!DOCTYPE html>' not in html:
            status = 0
        self.create_article_content(self.session, html, a_id,status)

        # 分析正文内容，提取图片
        soup = BeautifulSoup(html, "html.parser")
        images = soup.find_all('img')
        if images:
            for image in images:
                data_src = image.get('data-src')
                if data_src:
                    img_path = self.save_img(data_src)
                    if img_path:
                        self.create_article_img(self.session, a_id, img_path, data_src)
                src = image.get('src')
                if src:
                    img_path = self.save_img(src)
                    if img_path:
                        self.create_article_img(self.session, a_id, img_path, src)

        # 打印下
        print(str(article['time']) + ' ' + str(self.page) + ' ' + gzh['wechat_name'] + ' ' + article['title'])

    def run(self):
        # 创建搜狗爬虫
        ws_api = WechatSogouAPI()

        max_time = 0
        set_redis = False
        if self.check_time:
            # 取时间
            last_time = self.r.get(self.a_type)
            if not last_time:
                last_time = 0
            else:
                last_time = int(last_time)
            max_time = last_time

        # 开始爬取
        gzh_articles = getattr(ws_api, 'get_gzh_article_by_hot')(eval(self.m_type + self.a_type), self.page)
        for i in gzh_articles:
            gzh = i['gzh']
            article = i['article']

            if self.check_time:
                time_now = int(article['time'])
                if time_now > last_time:
                    # 将公众号放入redis,用于公众号文章爬取
                    self.r.lpush('gzh', gzh['wechat_name'] + '_' + self.a_type)
                    # 处理文章，图片
                    self.work(gzh, article)

                # 更新最后一次的爬取时间，避免重复爬取
                if time_now > max_time:
                    max_time = time_now
                    set_redis = True
            else:
                # 将公众号放入redis,用于公众号文章爬取
                self.r.lpush('gzh', gzh['wechat_name'] + '_' + self.a_type)
                # 处理文章，图片
                self.work(gzh, article)

        # 记录下爬取的页码
        page_name = self.a_type + '_page'
        self.r.set(page_name, self.page)

        if set_redis:
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
        '私房话': 'sifanghua',
        '八封精': 'gossip',
        '时尚圈': 'fashion',
    }

    args = sys.argv
    if len(args) > 1:
        page = 2
        while True:
            s = spider(args[1], page, False)
            s.run()
            page += 1
    else:
        for k in wxs:
            s = spider(wxs[k], 1,False)
            s.run()