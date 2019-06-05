## Python Chaperone

Chaperone is a wrapper for functions that are extremely long or embarrasingly parallel processes commonly used to solve problems in data science and web scraping. Chaperone provides additional functionality for managing or running those functions in a continuous fashion. 

## Features: 

* Track extremely long processes using a database
* Monitor errors
* Automatically retry errors
* Save results to database
* Leverages the excellent [ray project](https://ray.readthedocs.io/en/latest/) providing facilities for scaling up function performance using clusters of computers using AWS, GCP

## Concept:

1. Write a function that accepts a string parameter (or json, if you need to be more expressive)
2. The function should return something that is coercible to JSON (model results, text, a dictionary of numbers, a pandas dataframe)
3. Do not attempt to pass complex Python objects / classes into the function, create them inside the function otherwise [Ray's serialization of objects](https://ray.readthedocs.io/en/latest/serialization.html#what-objects-does-ray-handle) can fail

## Usage: 

```
from pychaperone.chaperone import chaperone
from pychaperone.db_setup import QueueCheck
from peewee import SqliteDatabase # or PostgreSQL or MySQL


# Setup db
db = SqliteDatabase("my.db")
db.connect()
db.create_tables([QueueCheck])
db.close()


def myfun(x):
    return x

ids = [1,2,3,4,5,6]

# Saves the results of myfun, given ids, as json in the db
# Single thread
chaperone(
    items=ids, 
    fun=myfun, 
    db='my.db', 
    db_fun=SqliteDatabase,
    save=True
)

# Multithread
chaperone_ray(
    items=ids,
    fun=myfun,
    db='my.db',
    db_fun=SqliteDatabase,
    save=True
)
```

Now you can check how successful your process was with ease

```
error_rate = len(QueueCheck.select().where(complete == False))/len(ids)

```