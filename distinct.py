#!/usr/bin/env python
# coding:utf8

"""
删除重复的文章
"""

import os,sys
from wechatsogou import WechatSogouAPI, WechatSogouConst
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import update


if __name__ == '__main__':
    # 初始化数据库连接
    engine = create_engine('mysql://root:123456@localhost:3306/wx?charset=utf8mb4')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # 删除重复文章
    # 检查是否有重复的
    a_dis = session.execute('select * from (select min(id) from article group by title having count(title) > 1) as b;')

    if a_dis.fetchall() == []:
        sys.exit(0)

    session.execute('delete from article where id not in (select * from (select min(id) from article '
                    'group by title having count(title) > 1) as b);')
    session.commit()

    # 删除重复正文
    session.execute('delete from article_content where article_id not in (select id from article);')
    session.commit()

    # 删除本地图片
    a_content = session.execute('select local from article_img where article_id not in (select id from article);')
    for i in a_content:
        os.system('rm -fr %s' % i[0])

    # 删除表格中的图片
    session.execute('delete from article_img where article_id not in (select id from article);')
    session.commit()

    session.close()