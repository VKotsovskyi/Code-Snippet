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
from model import User, Code, db
from datetime import date
import datetime

from playhouse.shortcuts import model_to_dict, dict_to_model

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/snippets/', Snippets)
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

        self.db = db

        self.db.create_tables([User, Code], True)


class BaseHandler(web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class Snippets(BaseHandler):

    def get(self):
        all_snippets = []
        codes = Code.select().join(User)
        for code in codes:
            code = model_to_dict(code)
            code['url'] = ("%s://%s/snippets/%s" %
                           (self.request.protocol,
                            self.request.host,
                            str(code['id'])))
            code['created_date'] = self.__date_handler(code['created_date'])
            all_snippets.append(code)
        self.write(json_encode(all_snippets))

    def __date_handler(self, obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj




if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
