from peewee import Model, TextField, DateField, BooleanField, SqliteDatabase, PostgresqlDatabase, DatabaseProxy
from playhouse.sqlite_ext import JSONField

database_proxy = DatabaseProxy()

# def db_setup(type='sqlite', user=None, password=None, host=None, port=None):
#     if type == 'sqlite':
#         db = SqliteDatabase('queuecheck.db')
    
#     if type == 'postgresql':
#         db = PostgresqlDatabase(
#             'queuecheck', 
#             user=user,
#             password=password,
#             host=host,
#             port=port
#         )

#     return(db)


class BaseModel(Model):
    class Meta:
        database = database_proxy

class QueueCheck(BaseModel):
    item = TextField(unique=True)
    function = TextField(default="")
    complete = BooleanField(default=True)
    error = TextField(default="")
    meta = JSONField(default="")
