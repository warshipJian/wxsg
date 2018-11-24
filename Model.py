#!/usr/bin/env python
#coding:utf8

'''
model类
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String,Integer

# 创建对象的基类:
Base = declarative_base()

# 文章表
class article(Base):
    # 表的名字:
    __tablename__ = 'article'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    wechat_name = Column(String(64))
    headimage = Column(String(256))
    abstract = Column(String(4096))
    main_img = Column(String(256))
    open_id = Column(String(32))
    time = Column(String(11))
    title = Column(String(256))
    url = Column(String(256))
    type = Column(String(16))
    headimage_local = Column(String(256))
    main_img_local = Column(String(256))

# 文章内容表
class article_content(Base):
    # 表的名字:
    __tablename__ = 'article_content'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer)
    content = Column(String)

# 文章图片表
class article_img(Base):
    # 表的名字:
    __tablename__ = 'article_img'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer)
    local = Column(String(256))
    url = Column(String(256))