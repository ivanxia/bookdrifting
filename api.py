# -*- coding: utf-8 -*-

import falcon
import os
import json
import httplib
from db import UserDB, BookDB
import schema
import logger

MAX_BOOKS_PER_UER = 4

BOOK_STATUS_MAP = {
    "release": 0,
    "frozen": 1,
    "reserved": 2,
    "all": None
}

LOG = logger.get_logger()


def validate_params(param, params):
    if param in params:
        return True, 'OK'
    else:
        raise Exception('Valid params are %s'%params.keys())

class User(object):
    def on_get(self, req, res):
        user = UserDB()
        users = user.list_user()

        LOG.info(("Users fectched: {0}.").format(json.dumps(users).decode("unicode-escape")))

        res.status = httplib.OK
        res.body = json.dumps(users)

    def on_post(self, req, res):
        data = req.stream.read()
        data = json.loads(data)

        sche = schema.Schema("user")
        sche.validate(data)

        desc = "Normal user"
        if 'description' in data:
            desc = data['description']

        role = 0
        if 'role' in data:
            role = data['role']

        user = UserDB()
        user.add_user(data['id'], data['name'], data['password'], role, desc)

        res.status = httplib.OK
        res.body = "User %s is created successfully" % data['name']


class UserSpecified(object):
    def on_put(self, req, res, userId):
        data = req.stream.read()
        data = json.loads(data)

        sche = schema.Schema("password")
        sche.validate(data)

        user = UserDB()
        user.change_password(userId, data['password'])

        res.status = httplib.OK
        res.body = "Password for user %s is changed successfully" % userId

    def on_delete(self, req, res, userId):
        user = UserDB()
        user.delete_user(userId)

        res.status = httplib.OK
        res.body = "User ID %s delete successfully" % userId


class Books(object):
    def on_get(self, req, res):
        status = None
        if 'status' in req.params:
            param = req.params['status']
            validate_params(param, BOOK_STATUS_MAP)
            status = BOOK_STATUS_MAP[param]

        book = BookDB()
        books = book.list_book(status=status)

        LOG.info(("Books for all users fectched: {0}.").format(json.dumps(books).decode("unicode-escape")))

        res.status = httplib.OK
        res.body = json.dumps(books)


class Book(object):
    def on_get(self, req, res, userId):
        status = None
        if 'status' in req.params:
            param = req.params['status']
            validate_params(param, BOOK_STATUS_MAP)
            status = BOOK_STATUS_MAP[param]

        book = BookDB()
        books = book.list_book(userId=userId, status=status)

        LOG.info(("Books as per user fectched: {0}.").format(json.dumps(books).decode("unicode-escape")))

        res.status = httplib.OK
        res.body = json.dumps(books)

    def on_post(self, req, res, userId):
        '''
            - check if user exists;
            - check if book exists;
            - check if book number reach maximum;
        '''
        data = req.stream.read()
        data = json.loads(data)

        sche = schema.Schema("book")
        sche.validate(data)

        # Check if user exists
        user = UserDB()
        user_checking = user.get_user(userId)
        if not user_checking:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "User Id %s not exists. Please create user first.\n" % userId
            return

        book = BookDB()
        # check if book already exists
        book_existing = book.get_book_by_name(userId, data['name'])
        if len(book_existing) != 0:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "Book %s has already existed." % data['name']
            return

        # check if book amount reach maximum
        counts = book.count_book(userId)
        if counts == MAX_BOOKS_PER_UER:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "Only %s books can be added. It reaches maximum." % MAX_BOOKS_PER_UER
            return

        # Add book to DB
        if counts == 0:
            bookId = 1
        else:
            bookId = 15
            books = book.list_book(userId)
            for ibook in books:
                bookId = bookId - ibook['ID']%10000

            for i in [1,2,4,8]:
                if bookId&i != 0:
                    bookId = i
                    break

        LOG.info(("Book relative ID: [{0}]").format(bookId))

        status = 0
        if 'status' in data:
            status = data['status']

        desc = data['name']
        if desc in data:
            desc = data['description']

        bookId = 10000*int(userId)+bookId
        book.add_book(userId, bookId, data['name'], status, desc)

        res.status = httplib.OK
        res.body = "Book %s is added successfully" % data['name']


class BookSpecified(object):
    def on_delete(self, req, res, userId, bookName):
        book = BookDB()
        book.delete_book(userId, bookName)

        res.status = httplib.OK
        res.body = "Book %s delete successfully" % bookName

    def on_put(self, req, res, userId, bookName):
        book = BookDB()

        data = req.stream.read()
        data = json.loads(data)

        myBook = book.get_book_by_name(userId, bookName)

        updatedBook = myBook[0]
        if 'id' in data:
            updatedBook['ID'] = data['id']
        if 'status' in data:
            updatedBook['Status'] = data['status']
        if 'description' in data:
            updatedBook['Description'] = data['description']

        book.update_book(userId, updatedBook['ID'], bookName, updatedBook['Status'], updatedBook['Description'])

        res.status = httplib.OK
        res.body = "Book %s updated successfully" % bookName

        '''
class BookKept(object):
    def on_get(self, req, res, userId):
        book = BookDB()
        keptBooks = book.list_book_kept(userId)

        res.status = httplib.OK
        res.body = json.dumps(keptBooks)
        '''


class BookReserve(object):
    def on_post(self, req, res, userId):
        data = req.stream.read()
        data = json.loads(data)

        sche = schema.Schema("book_reserve")
        sche.validate(data)

        book = BookDB()

        # check if exceeds the maximum books
        resvd = book.list_book_reserved(userId)

        print len(resvd)

        if len(data['books'])+len(resvd) > MAX_BOOKS_PER_UER:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "You can only reserve %s books now." % (MAX_BOOKS_PER_UER-len(resvd))
            return

        ret = book.book_reserve(userId, data['books'])
        if not ret:
            res.status = httplib.OK
            res.body = "All books reserved."
        else:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "Books failed to reserve: %s" % ret

    def on_put(self, req, res, userId):
        data = req.stream.read()
        data = json.loads(data)

        sche = schema.Schema("book_reserve")
        sche.validate(data)

        book = BookDB()

        ret = book.book_unreserve(userId, data['books'])
        if not ret:
            res.status = httplib.OK
            res.body = "All books unreserved."
        else:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "Books failed to unreserve: %s" % ret
