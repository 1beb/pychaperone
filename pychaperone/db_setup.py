from peewee import Model, TextField, DateField, BooleanField, SqliteDatabase
from playhouse.sqlite_ext import JSONField

class QueueCheck(Model):
    item = TextField(unique=True)
    function = TextField(default="")
    complete = BooleanField(default=True)
    error = TextField(default="")
    meta = JSONField(default="")

    class Meta: 
        database = db
