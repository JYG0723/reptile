# created by 10412
# !/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-01-18 15:19
# Project: V2EX

import random

import MySQLdb
from pyspider.libs.base_handler import *

# 爬太快的话会封掉
class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'root', 'exchange', charset='utf8')  # 1. 先把db建起来链接

    def add_question(self, title, content):
        try:
            cursor = self.db.cursor()   # 2. 取一个游标，要进行一次操作了
            sql = 'insert into exchange_question(title, content, user_id, create_time, update_time, comment_count) values ("%s","%s",%d, %s, %s, %d)' % (
                title, content, random.randint(54, 63), 'now()', 'now()', 0);   # 3. 一个sql语句
            print sql
            cursor.execute(sql)
            print cursor.lastrowid  # 4. 用游标对象执行sql语句操作
            self.db.commit()    # 5. 执行之后，commit一下，然后根据你sql语句所执行的操作就能获取数据库当中的内容。相当于git中的add再commit
        except Exception, e:
            print e
            self.db.rollback()

    @every(minutes=24 * 60)   # 这里进来
    def on_start(self):
        self.crawl('https://www.v2ex.com/', callback=self.index_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)  # 大板块
    def index_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/?tab="]').items():  # 这里原本默认要把所有的http请求过来。我们不能这么写，因为我们第一层是要爬所有的带参数tab的
            self.crawl(each.attr.href, callback=self.tab_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)  # css选择器找到小版块
    def tab_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/go/"]').items():
            self.crawl(each.attr.href, callback=self.board_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)  # 再找到帖子
    def board_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/t/"]').items(): # 解析当前页面
            url = each.attr.href
            if url.find('#reply') > 0:
                url = url[0:url.find('#')]  # 去重，防止如果帖子发生变法。比如再有人评论的话，那么可能会出现重复爬去的情况。
            self.crawl(url, callback=self.detail_page, validate_cert=False)
        for each in response.doc('a.page_normal').items():  #翻页的页面
            self.crawl(each.attr.href, callback=self.board_page, validate_cert=False)

    @config(priority=2) # 把帖子中的东西解析出来
    def detail_page(self, response):
        title = response.doc('h1').text()
        content = response.doc('div.topic_content').html().replace('"', '\\"')  # 这里内容就取出来了。
        self.add_question(title, content)  # 通过数据库把它插进去
        # 这里再把评论也爬去一下，然后类似知乎的内个，插到数据库中
        return {
            "url": response.url,
            "title": title,
            "content": content,
        }
