# -*- coding: utf-8 -*-

import os
import pymysql.cursors
from DBUtils.PooledDB import PooledDB
import logger
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_DATEBASE = 'bookdrifting'
DB_CHARSET = 'utf8mb4'

# mincached : 启动时开启的闲置连接数量(缺省值 0 以为着开始时不创建连接)
DB_MIN_CACHED = 10

# maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
DB_MAX_CACHED = 10

# maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
DB_MAX_SHARED = 20

# maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
DB_MAX_CONNECYIONS = 100

# blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......>;
# 其他代表阻塞直到连接数减少,连接被分配)
DB_BLOCKING = True

# maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
DB_MAX_USAGE = 0

# setsession : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
DB_SET_SESSION = None


BOOK_RELEASE = 0
BOOK_RESERVED = 1
BOOK_FROZEN = 2

LOG = logger.get_logger()


class DBClient(object):
    def __init__(self):
        self.connection = None
        self.cursor = None

    def _init_con_(self):
        '''self.connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            db='bookdrifting',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)'''

        self.__pool = PooledDB(
            creator=pymysql,
            mincached=DB_MIN_CACHED,
            maxcached=DB_MAX_CACHED,
            maxshared=DB_MAX_SHARED,
            maxconnections=DB_MAX_CONNECYIONS,
            blocking=DB_BLOCKING,
            maxusage=DB_MAX_USAGE,
            setsession=DB_SET_SESSION,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            passwd=DB_PASSWORD,
            db=DB_DATEBASE,
            use_unicode=False,
            charset=DB_CHARSET)

        self.connection = self.__pool.connection()
        self.cursor = self.connection.cursor()

    def run_commit(self, sql):
        self._init_con_()
        ar = self.cursor.execute(sql)
        self.connection.commit()
        self.connection.close()
        return ar

    def run_show(self, sql, one=False):
        self._init_con_()
        self.cursor.execute(sql)

        if one:
            results = self.cursor.fetchone()
        else:
            results = self.cursor.fetchall()

        self.connection.close()
        return results

    def run_multi_commits(self, sqls):
        self._init_con_()
        with self.cursor:
            for sql in sqls:
                ret = self.cursor.execute(sql)

        self.connection.commit()
        self.connection.close()


'''
    User record format:
        ID
        Name
        Password
        Description
        Role
        CreateTime
        ModifyTime
'''


class UserDB(DBClient):
    def __init__(self):
        super(UserDB, self).__init__()

    def list_user(self):
        sql = "SELECT * FROM `user`"
        LOG.info(("List user sql: [{0}].").format(sql))

        rows = self.run_show(sql)

        users = []
        for row in rows:
            user = {
                "ID": row[0],
                "Name": row[1],
                "Description": row[3],
                "Role": row[4],
                "CreateTime": str(row[5]),
                "ModifyTime": str(row[6])
            }
            users.append(user)

        return users

    def add_user(self, id, name, passwd, role, desc):
        print "in db.... sql write..."
        sql = "INSERT INTO `user` (`id`, `name`, `password`, `role`, `description`, `CreateTime`, `ModifyTime`) "\
            "VALUES ('%s', '%s', '%s', '%s', '%s', now(), now())" % (id, name, passwd, role, desc)

        LOG.info(("Add user sql: [{0}].").format(sql))

        self.run_commit(sql)

    def delete_user(self, id):
        sql = "DELETE FROM `user` WHERE `ID`= '%s'" % (id)
        LOG.info(("Delete user sql: [{0}].").format(sql))

        self.run_commit(sql)

    def get_user(self, userId):
        sql = "SELECT * FROM `user` WHERE `id`=%s" % userId

        row = self.run_show(sql)

        user = {}
        if row:
            user = {
                "ID": row[0][0],
                "Name": row[0][1],
                "Description": row[0][3],
                "Role": row[0][4]
            }
        return user

    def change_password(self, userId, password):
        sql = "UPDATE `user` SET `Password`='%s', `ModifyTime`=now() WHERE `ID`='%s'" % (
            password, userId)

        LOG.info(("Change password sql: [{0}] ").format(sql))

        self.run_commit(sql)


'''
    Book record format:
        ID
        OwnerId
        Name
        Status
        Description
        KeeperId
        CreateTime
        ModifyTime
'''


class BookDB(DBClient):
    def __init__(self):
        super(BookDB, self).__init__()

    def list_book(self, userId=0, status=None):
        '''
            if userId == 0:
                return all books based on status
            else:
                return books as per userId and status
        '''

        if userId != 0:
            if not status:
                sql = "SELECT * FROM `book` WHERE `OwnerId`='%s' " % userId
            else:
                sql = "SELECT * FROM `book` WHERE `OwnerId`='%s' AND `Status`=%s" % (
                    userId, status)

            LOG.info(("List books as per userId sql: [{0}]").format(sql))
        else:
            if not status:
                sql = "SELECT * FROM `book`"
            else:
                sql = "SELECT * FROM `book` WHERE `Status`=%s" % (status)

            LOG.info(("List books sql: [{0}]").format(sql))

        books = []
        rows = self.run_show(sql)

        for row in rows:
            book = {
                "ID": row[0],
                "OwnerId": row[1],
                "Name": row[2],
                "Status": row[3],
                "Description": row[4],
                "keeperId": row[5],
                "CreateTime": str(row[6]),
                "ModifyTime": str(row[7])
            }
            books.append(book)

        return books

    def get_book_by_name(self, userId, bookName):
        sql = "SELECT * FROM `book` WHERE `OwnerId`='%s' AND `Name`='%s'" % (
            userId, bookName)

        LOG.info(("Get book sql: [{0}]").format(sql))

        row = self.run_show(sql)

        book = {}
        if row:
            book = {
                "ID": row[0][0],
                "OwnerId": row[0][1],
                "Name": row[0][2],
                "Status": row[0][3],
                "Description": row[0][4]
            }
        return book

    def get_book_by_id(self, bookId):
        sql = "SELECT * FROM `book` WHERE `OwnerId`='%s' AND `Name`='%s'" % (
            userId, bookName)

        LOG.info(("Get book sql: [{0}]").format(sql))

        row = self.run_show(sql)

        book = {}
        if row:
            book = {
                "ID": row[0][0],
                "OwnerId": row[0][1],
                "Name": row[0][2],
                "Status": row[0][3],
                "Description": row[0][4]
            }
        return book

    def count_book(self, userId):
        sql = "SELECT COUNT(*) FROM `book` WHERE `OwnerId`=%s" % userId

        LOG.info(("Count books sql: [{0}]").format(sql))

        row = self.run_show(sql)
        print row[0][0]
        return row[0][0]

    def add_book(self, userId, bookId, name, status=0, desc=None):
        sql = "INSERT INTO `book` (`OwnerId`, `ID`, `Name`, `Status`, `Description`, `KeeperId`, `CreateTime`, `ModifyTime`) "\
            "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', now(), now())" % (userId, bookId, name, status, desc, userId)

        LOG.info(("Add book sql: [{0}]").format(sql))

        self.run_commit(sql)

    def release_all_books(self):
        sql = "UPDATE `book` SET `Status`=0"

        LOG.info(("Release all books sql: [{0}]").format(sql))

        self.run_commit(sql)

    def update_book(self, userId, bookId, name, status=0, desc=None):
        sql = "UPDATE `book` SET `ID`='%s', `Status`='%s', `Description`='%s', `ModifyTime`=now() "\
            "WHERE `OwnerId`=%s and `Name`='%s'" % (bookId, status, desc, userId, name)

        LOG.info(("Update book sql: [{0}]").format(sql))

        self.run_commit(sql)

    def delete_book(self, userId, bookName):
        sql = "DELETE FROM `book` WHERE `OwnerId`=%s and `Name`='%s'" % (
            userId, bookName)

        LOG.info(("Delete book sql: [{0}]").format(sql))

        self.run_commit(sql)

        '''
        sqls = []
        s = "update book set status =12 where id=260001"
        sqls.append(s)
        #s = "update update user set status =3 where userid='23'"
        # sqls.append(s)

        print sqls
        self.run_multi_commits(sqls)
        '''

    def list_book_kept(self, userId):
        sql = "SELECT * FROM `book` WHERE `KeeperId`=%s AND `Status`=%s " % (
            userId, BOOK_FROZEN)

        LOG.info(("List books kept sql: [{0}]").format(sql))

        rows = self.run_show(sql)
        kept_books = []
        for row in rows:
            kept_book = {
                "KeeperId": row[5],
                "BookId": row[0],
                "BookName": row[2]
            }
            kept_books.append(kept_book)
        return kept_books

    def list_book_reserved(self, userId):
        sql = "SELECT * FROM `book` WHERE `KeeperId`=%s AND `Status`=%s " % (
            userId, BOOK_RESERVED)

        LOG.info(("List books reserved sql: [{0}]").format(sql))

        rows = self.run_show(sql)
        rsvd_books = []
        for row in rows:
            rsvd_book = {
                "KeeperId": row[5],
                "BookId": row[0],
                "BookName": row[2]
            }
            rsvd_books.append(rsvd_book)
        return rsvd_books

    def book_reserve(self, userId, books):
        resvFailedBooks = []
        for book in books:
            sql = "UPDATE `book` SET `Status`=%s, `KeeperId`=%s WHERE `ID`=%s AND `status`=%s" % (
                BOOK_RESERVED, userId, book['id'], BOOK_RELEASE)
            LOG.info(("Reserve book sql: [{0}]").format(sql))

            affectedRow = self.run_commit(sql)
            if affectedRow == 0:
                resvFailedBooks.append(book['name'])

        return resvFailedBooks

    def book_unreserve(self, userId, books):
        unresvFailedBooks = []
        for book in books:
            sql = "UPDATE `book` SET `Status`=%s, `KeeperId`=OwnerId WHERE `ID`=%s AND `KeeperId`=%s" % (
                BOOK_RELEASE, book['id'], userId)

            LOG.info(("Unreserve book sql: [{0}]").format(sql))

            affectedRow = self.run_commit(sql)
            if affectedRow == 0:
                unresvFailedBooks.append(book['name'])

        return unresvFailedBooks
