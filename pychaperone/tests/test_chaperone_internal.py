from unittest import TestCase
from datetime import datetime
from peewee import SqliteDatabase
from pychaperone.db_setup import QueueCheck
from pychaperone.chaperone import chaperone_internal
import os

db = SqliteDatabase(':memory:')
db.connect()
db.create_tables([QueueCheck])
db.close()

class TestChaperoneInternal(TestCase):

    def f1(self, x):
        return [x]

    def f2(self, x):
        return datetime.today()

    def f3(self,x):
        return ValueError

    
    items = [1,2,3,4]
    items_fail = [5,6,7]

    db = ':memory:'
    db_fun = 'sqlite'

    def test_chaperone_one_fails(self):
        res = chaperone_internal(
            item=1, 
            fun=self.f3,
            db=self.db,
            db_fun=self.db_fun,
            save=False
        )

        self.assertEqual(res, ValueError)

    def test_chaperone_one_nosave(self):
        res = chaperone_internal(
            item=1, 
            fun=self.f1, 
            db=self.db,
            db_fun=self.db_fun,
            save=False
        )

        self.assertEqual(res,[1])

    def test_chaperone_returns_errors(self):
        res = chaperone_internal(
            item=1,
            fun=self.f3,
            db=self.db,
            db_fun=self.db_fun, 
            save=False
        )
        self.assertEqual(res, ValueError)

    
    def test_chaperone_one_nosave_nosql(self):
        QueueCheck.delete().where(QueueCheck.item.in_([1,2,3,4,5,6,7])).execute()
        chaperone_internal(
            item=1, 
            fun=self.f1, 
            db=self.db,
            db_fun=self.db_fun,
            save=False
        )

        self.assertTrue(len(QueueCheck.select()) == 0)
    
    def test_chaperone_one_save(self):
        QueueCheck.delete().where(QueueCheck.item.in_([1,2,3,4,5,6,7])).execute()
        chaperone_internal(
            item=1, 
            fun=self.f1, 
            db=self.db,
            db_fun=self.db_fun,
            save=True
        )

        res = QueueCheck.select().where(QueueCheck.item == '1').get()
        self.assertEqual(res.item, '1')
        self.assertEqual(res.error, '')
        self.assertEqual(res.complete, True)
        self.assertEqual(res.meta,'[1]')
        QueueCheck.delete().where(QueueCheck.item == '1').execute()
