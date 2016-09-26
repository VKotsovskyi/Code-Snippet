import os.path

import base64
import uuid
import json

import tornado
from tornado.escape import json_encode
import tornado.httpserver
import tornado.ioloop
from tornado import web
from tornado import gen
from peewee import *
from model import Users, Code, db
from datetime import date
import datetime

from playhouse.shortcuts import model_to_dict, dict_to_model

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/snippets/$', Snippets),
            (r'/snippets/(\d*|)/$', CurrentSnippet)
        ]

        settings = dict(
            todo_title=u"Code",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            login_url="/auth/login",
            debug=True,
        )

        super(Application, self).__init__(handlers, **settings)

        self.db = db

        self.db.connect()
        self.db.create_tables([Users, Code], True)


class BaseHandler(web.RequestHandler):
    @property
    def db(self):
        self.application.db.connect()
        return self.application.db


class Snippets(BaseHandler):
    def get(self):
        all_snippets = []
        codes = Code.select().join(Users)
        for code in codes:
            code = model_to_dict(code)
            code['url'] = ("%s://%s/snippets/%s/" %
                           (self.request.protocol,
                            self.request.host,
                            str(code['id'])))
            code['created_date'] = Helpers.date_handler(code['created_date'])
            all_snippets.append(code)
        self.write(json_encode(all_snippets))
        self.set_header('Content-Type', 'application/json')

    def post(self):
        snippet = json.loads(self.request.body)
        if snippet['owner'] and snippet['title'] and snippet['code']\
                and snippet['linenos'] and snippet['language'] and snippet['style']:
            with db.transaction() as transaction:
                try:
                    code = Code(**snippet)
                    code.save()
                except:
                    transaction.rollback()
            code_result = model_to_dict(Code.get(Code.id == model_to_dict(code)['id']))
            code_result['created_date'] = Helpers.date_handler(code_result['created_date'])
            self.write(code_result)
        else:
            self.write(json_encode('All fields are required'))


class CurrentSnippet(BaseHandler):
    def get(self, snippet):
        if snippet:
            code = model_to_dict(Code.get(Code.id == snippet))
            code['created_date'] = Helpers.date_handler(code['created_date'])
            self.write(code)

    def put(self, snippet):
        if snippet:
            arguments = json.loads(self.request.body)
            code_write = Code.update(**arguments).where(Code.id == snippet)
            code_write.execute()
            code = model_to_dict(Code.get(Code.id == snippet))
            code['created_date'] = Helpers.date_handler(code['created_date'])
            self.write(code)

    def delete(self, snippet):
        if snippet:
            code_write = Code.get(Code.id == snippet)
            code_write.delete_instance()
            self.write('')


class Helpers():

    @staticmethod
    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
