from peewee import *
import datetime

class User(Model):
    username = CharField(unique=True)


class Code(Model):
    owner = ForeignKeyField(User, related_name='codes')
    title = TextField()
    code = TextField()
    linenos = BooleanField(default=True)
    language = TextField()
    style = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
