from peewee import Model, TextField, DateField, BooleanField, SqliteDatabase, PostgresqlDatabase, DatabaseProxy
from playhouse.sqlite_ext import JSONField
import datetime 

database_proxy = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = database_proxy

class QueueCheck(BaseModel):
    item = TextField(unique=True)
    function = TextField(default="")
    complete = BooleanField(default=True)
    error = TextField(default="")
    meta = JSONField(default="")
    created_date = DateField(default=datetime.datetime.now())
