"""
The goal of chaperone is to make it easier to do work once. Frequently
we have scripts that scrape data from the web, but when a part of the function
fails, we have to start from the beginning again, wasting time. In order to
relegate this problem we add link tracking and error capture so that we can 
re-run failures. There are often intermediate steps to get to those data of 
interest, this system is designed to track those intermediate steps as well.

Code Overview: 

1. Get or create a database object using the target URL
2. Run some predefined function on that URL "fun"
3. Arbitrarily store the data
4. If failures occur, retry the code (assuming updates to "fun")
"""

from pychaperone.db_setup import QueueCheck
from json import dumps
from peewee import IntegrityError, SqliteDatabase, PostgresqlDatabase
import ray


def chaperone(items, fun, db, db_fun='sqlite', save=True):

    if isinstance(items, list):
        
        res = [chaperone_internal(item, fun, db, db_fun, save) for item in items]

        if any(isinstance(el, list) for el in res):
            res = [val for sublist in res for val in sublist]

    else:
        raise ValueError('It appears you have passed something that is not a list')

    if(all(item is None for item in res)):
        return None
    else:
        return res


def chaperone_internal(item, fun, db, db_fun, save, force=False):

    fname = fun.__name__

    meta = None
    
    if db_fun == 'sqlite':
        db = SqliteDatabase(db)


    
    if db_fun == 'postgres':
        db = PostgresqlDatabase(            
            db['dbname'], 
            user=db['user'], 
            password = db['password'], 
            host = db['host'], 
            port=db['port']
        )

    db.connect()

    try:
        with db.atomic():
            # Here we create an instance instead of a record
            # If save=False, we need not create a record in the 
            # db
            if save is False:
                check = QueueCheck(item=item, complete=False, function=fname)
            else: 
                check = QueueCheck.create(item=item, complete=False, function=fname)

    except IntegrityError:
        check = QueueCheck.get(QueueCheck.item==item, QueueCheck.function==fname)

    try:    

        if check.complete is False or force is True:
            meta = fun(item)

            if save is True: 
                # Data is expected to be in a pandas data frame or 
                # a dictionary, in both cases ready to be converted
                # to json. We use json to take advantage of postgres 
                check.meta = dumps(meta)

                check.complete = True
                check.error = '' # Reset error message for posterity
                check.save()
            else: 
                return meta

    except Exception as e:
        if save is True:
            check.item = item
            check.complete = False
            check.error = str(e)
            check.save()
        else:
            return e

    db.close()

# Ray Version

@ray.remote
def chaperone_internal_ray(item, fun, db, db_fun, save, force=False): # pragma: no cover
    return chaperone_internal(item, fun, db, db_fun, save, force)

def chaperone_ray(items, fun, db, db_fun='sqlite', save=True): # pragma: no cover

    if isinstance(items, list):

        res = ray.get(
            [chaperone_internal_ray.remote(item, fun, db, db_fun, save) for item in items]
        )

        if any(isinstance(el, list) for el in res):
            res = [val for sublist in res for val in sublist]

    else:
        raise ValueError('It appears you have passed something that is not a list')

    if(all(item is None for item in res)):
        return None
    else:
        return res