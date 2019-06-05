from unittest import TestCase
from datetime import datetime
from peewee import SqliteDatabase
from pychaperone.db_setup import QueueCheck
from pychaperone.chaperone import chaperone
import dill as pickle
import os

db = SqliteDatabase(':memory:')
db.connect()
db.create_tables([QueueCheck])
db.close()

class TestChaperoneIntegration(TestCase):

    def f1(self, x):
        return [x]

    def f2(self, x):
        return datetime.today()

    def f3(self,x):
        return ValueError

    def f4(self,x):
        return None
    
    def f5(self,x):
        return [[x]]

    
    items = [1,2,3,4]
    items_fail = [5,6,7]

    db = ':memory:'
    db_fun = 'sqlite'

    def test_chaperon_all_none(self):
        res = chaperone(
            items=self.items,
            fun=self.f4,
            db=self.db,
            db_fun=self.db_fun, 
            save=False
        )
        self.assertEqual(res, 
            None)

    def test_chaperone_except_get(self):

        def failure(x):
            return datetime.today()
        
        def passer(x):
            return [x]

        # We rename the function to failure so it gets captured appropriately by chaperone
        passer.__name__ = 'failure'
        
        chaperone(
            items=self.items_fail,
            fun=failure,
            db=self.db,
            db_fun=self.db_fun, 
            save=True
        )

        res = QueueCheck.select().where(QueueCheck.item.in_(['5', '6', '7']))

        for i in res:
            self.assertEqual(i.error , 'Object of type datetime is not JSON serializable')
            self.assertEqual(i.complete, False)
            self.assertEqual(i.function, "failure")

        chaperone(
            items=self.items_fail,
            fun=passer,
            db=self.db,
            db_fun=self.db_fun, 
            save=True
        )        

        res = QueueCheck.select().where(QueueCheck.item.in_(['5', '6', '7']))
        for i in res:
            self.assertEqual(i.error , '')
            self.assertEqual(i.complete, True)
            self.assertEqual(i.function, "failure")

        QueueCheck.delete().where(QueueCheck.item.in_(['5', '6', '7'])).execute()

    def test_passes_back_errors(self):
        res = chaperone(
            items=self.items,
            fun=self.f3,
            db=self.db,
            db_fun=self.db_fun, 
            save=False
        )
        for i in res:
            self.assertEqual(i, ValueError)

    def test_chaperone_flattens_list(self):
        def myfun(x):
            return [1,2,3]

        res = chaperone(
            items=[1,2],
            fun=myfun,
            db=self.db,
            db_fun=self.db_fun, 
            save=False
        )
        self.assertEqual(res, [1,2,3,1,2,3])

    def test_chaperone_json_result(self):
        chaperone(
            items=self.items,
            fun=self.f1,
            db=self.db,
            db_fun=self.db_fun, 
            save=True
        )

        res = QueueCheck.select().where(QueueCheck.item.in_(['1', '2', '3', '4']))        
        for i in res:
            self.assertEqual(i.error , '')
            self.assertEqual(i.complete, True)
            self.assertEqual(i.function, "f1")
            
        for i in zip(res, ['[1]', '[2]', '[3]','[4]']):
            self.assertEqual(
                i[0].meta, i[1]
            )

        QueueCheck.delete().where(QueueCheck.item.in_(['1', '2', '3', '4'])).execute()

    def test_chaperone_fails_nolist(self):
        with self.assertRaises(ValueError):
            chaperone(
                items=1,
                fun=self.f1,
                db=self.db,
                db_fun=self.db_fun, 
                save=False
            )

    def test_chaperone_cant_convert_to_json_fails(self):
        chaperone(
            items=self.items_fail, 
            fun=self.f2,
            db=self.db,
            db_fun=self.db_fun,
            save=True
        )

        res = QueueCheck.select().where(QueueCheck.item.in_(['5', '6', '7']))
        for i in res:
            self.assertEqual(i.error , 'Object of type datetime is not JSON serializable')
            self.assertEqual(i.complete, False)
            self.assertEqual(i.function, "f2")
        QueueCheck.delete().where(QueueCheck.item.in_(['5', '6', '7'])).execute()