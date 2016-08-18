import os.path

import base64
import uuid
import psycopg2
import momoko

import tornado
from tornado.escape import json_encode
import tornado.httpserver
import tornado.ioloop
from tornado import web
from tornado import gen
from peewee import *
from model import User, Code
from datetime import date
import datetime

from local_setting import USERNAME, PASSWORD

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/', Home)
        ]

        settings = dict(
            todo_title=u"Code",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            login_url="/auth/login",
            debug=True,
        )

        super(Application, self).__init__(handlers, **settings)

        self.db = PostgresqlDatabase('codesnippet', user=USERNAME, password=PASSWORD)
        User.create_table(True)
        Code.create_table(True)


class BaseHandler(web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class Home(BaseHandler):
    def get(self):
        code = Code.get()
        self.write(json_encode({}))


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
