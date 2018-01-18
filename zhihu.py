#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-01-18 18:17
# Project: zhihu

from pyspider.libs.base_handler import *
import random
import MySQLdb


# 不把自己伪装成Google爬虫的会封掉。所以都要Log
class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v1',
        'headers': {
            'User-Agent': 'GoogleBot',
            'Host': 'www.zhihu.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
    }

    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'root', 'exchange', charset='utf8')  # 1. 先把db建起来链接

    def add_question(self, title, content, comment_count):
        try:
            cursor = self.db.cursor()
            sql = 'insert into exchange_question(title, content, user_id, create_time, update_time, comment_count) values ("%s","%s",%d, %s, %s, %d)' % (
                title, content, random.randint(54, 63), 'now()', 'now()', 0);  # 3. 一个sql语句
            # print sql
            cursor.execute(sql)
            qid = cursor.lastrowid
            self.db.commit()
            return qid
        except Exception, e:
            print e
            self.db.rollback()
        return 0

    def add_comment(self, qid, comment):
        try:
            cursor = self.db.cursor()
            sql = 'insert into comment(content, entity_type, entity_id, user_id, created_date) values ("%s",%d,%d, %d,%s)' % (
            comment, 1, qid, random.randint(1, 10), 'now()');
            # print sql
            cursor.execute(sql)
            self.db.commit()
        except Exception, e:
            print e
            self.db.rollback()

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.zhihu.com/topic/19554298/top-answers?page=3', callback=self.index_page,
                   validate_cert=False)
        self.crawl('https://www.zhihu.com/topic/19552330/top-answers?page=3', callback=self.index_page,
                   validate_cert=False)

    @config(age=10 * 24 * 60 * 60)  # 把这个东西爬下来
    def index_page(self, response):
        for each in response.doc('a.question_link').items():
            self.crawl(each.attr.href, callback=self.detail_page, validate_cert=False)
        for each in response.doc('.zm-invite-pager span a').items():
            self.crawl(each.attr.href, callback=self.index_page, validate_cert=False)

    @config(priority=2)  # 解析页面的detail
    def detail_page(self, response):
        items = response.doc('div.zm-editable-content.clearfix').items()  # 取评论
        title = response.doc('span.zm-editable-content').text()  # 取标题

        html = response.doc('#zh-question-detail .zm-editable-content').html()  # Html取出来
        if html == None:  # 根据页面报错的情况，调整代码。这相当于处理异常的地方
            html = response.doc('#zh-question-detail .content.hidden').html()
            if html == None:
                html = ''

        content = html.replace('"', '\\"')
        print content

        qid = self.add_question(title, content, sum(1 for x in items))  # 问题入库
        for each in response.doc('div.zm-editable-content.clearfix').items():  # 把所有的评论爬取下来
            self.add_comment(qid, each.html().replace('"', '\\"'))  # 把评论也加上

        return {
            "url": response.url,
            "title": title,
            "content": content,
        }
