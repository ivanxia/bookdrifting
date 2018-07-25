import falcon
import os
import json
import httplib
from db import UserDB, BookDB, BookKeptDB
import schema
import logger

MAX_BOOKS_PER_UER = 4
BOOK_RELEASE = 0
BOOK_RESERVED = 1
BOOK_FROZEN = 2

LOG = logger.get_logger()

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

class Book(object):
    def on_get(self, req, res, userId):
        book = BookDB()
        books = book.list_book(userId)

        print "----00-00-0-0-00-"
        print type(books)
        LOG.info(("Books fectched: {0}.").format(books))
        #LOG.info(("Books fectched: {0}.").format(json.dumps(books).decode("unicode-escape")))

        res.status = httplib.OK
        res.body = json.dumps(books)

    def on_post(self, req, res, userId):
        data = req.stream.read()
        data = json.loads(data)

        print "----------0000-------------"

        # Check if user exists
        user = UserDB()
        user_checking = user.get_user(userId)
        if not user_checking:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "User Id %s not exists. Please create user first.\n" % userId
            return

        print "----------0000-1-------------"

        sche = schema.Schema("book")
        sche.validate(data)

        status = 0
        if 'status' in data:
            status = data['status']

        desc = data['name']
        if desc in data:
            desc = data['description']

        print "----------1-------------"
        book = BookDB()

        # check if book already exists
        book_existing = book.get_book(userId, data['name'])
        if len(book_existing) != 0:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "Book %s has already existed." % data['name']
            return
        print "----------2-------------"

        # check if book amount reach maximum
        counts = book.count_book(userId)
        #counts = counts[0]['COUNT(*)']
        if counts == MAX_BOOKS_PER_UER:
            res.status = httplib.INTERNAL_SERVER_ERROR
            res.body = "Only %s books can be added. It reaches maximum." % MAX_BOOKS_PER_UER
            return
        print "----------3-------------"

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
        print "----------4-------------"

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

        myBook = book.get_book(userId, bookName)

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


class BookKept(object):
    def on_get(self, userId):
        bookKept = BookKeptDB()
        keptBooks = bookKept.list_book_kept(userId)

        res.status = httplib.OK
        res.body = json.dumps(keptBooks)


class BookReserve(object):
    def on_get(self, userId):
        pass
