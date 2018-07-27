
import os
import falcon
from errors import handle_exceptions
from middlewares import MiddleWares
from api import User, UserSpecified
from api import Books, Book, BookSpecified
#from api import BookKept
from api import BookReserve

app = falcon.API(middleware=MiddleWares())

user = User()
user_one = UserSpecified()
books = Books()
book = Book()
book_one = BookSpecified()
#book_kept = BookKept()
book_reserve = BookReserve()

app.add_route('/v1/user', user)
app.add_route('/v1/user/{userId}', user_one)

app.add_route('/v1/books', books)
app.add_route('/v1/user/{userId}/book', book)

app.add_route('/v1/user/{userId}/book/{bookName}', book_one)
#app.add_route('/v1/user/{userId}/book_kept', book_kept)
app.add_route('/v1/user/{userId}/book_reserve', book_reserve)

app.add_error_handler(Exception, handler=handle_exceptions)
