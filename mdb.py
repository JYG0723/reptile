import MySQLdb

if __name__ == '__main__':
    db = MySQLdb.connect('localhost', 'root', 'root', 'exchange', charset='utf8')
    try:
        cursor = db.cursor()
        '''
        insertSql = 'INSERT INTO exchange_question(title,content,user_id,comment_count,create_time,update_time) VALUES("hikari","hikariNihao",49,0,now(),now())'
        cursor.execute(insertSql)
        qid = cursor.lastrowid
        db.commit()
        print qid
        '''

        selectSql = 'SELECT * FROM exchange_question ORDER BY id DESC LIMIT 2'
        cursor.execute(selectSql)

        for each in cursor.fetchall():
            for row in each:
                print row
            # print each

        db.commit()
    except Exception, e:
        print e
        db.rollback()
    db.close()
