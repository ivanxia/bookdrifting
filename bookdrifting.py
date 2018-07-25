
import os
import falcon
from errors import handle_exceptions
from middlewares import MiddleWares
from api import User, UserSpecified
from api import Book, BookSpecified
from api import BookKept

app = falcon.API(middleware=MiddleWares())

user = User()
user_one = UserSpecified()
book = Book()
book_one = BookSpecified()
book_kept = BookKept()

app.add_route('/v1/user', user)
app.add_route('/v1/user/{userId}', user_one)
app.add_route('/v1/user/{userId}/book', book)
app.add_route('/v1/user/{userId}/book/{bookName}', book_one)
app.add_route('/v1/user/{userId}/book_kept', book_kept)

app.add_error_handler(Exception, handler=handle_exceptions)
