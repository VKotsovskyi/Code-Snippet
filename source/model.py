from peewee import *
import datetime
from local_setting import USERNAME, PASSWORD
import datetime

db = PostgresqlDatabase('codesnippet', user=USERNAME, password=PASSWORD)

class User(Model):
    username = CharField(unique=True)

    class Meta:
        database = db
        order_by = ('username',)


class Code(Model):
    owner = ForeignKeyField(User, related_name='codes')
    title = TextField()
    code = TextField()
    linenos = BooleanField(default=True)
    language = TextField()
    style = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
