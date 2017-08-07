PseuDB
----

|Build Status| |Coverage| |Version|


PseuDB is inspired by TinyDB_ and lowdb_. It is a lightweight document 
oriented database optimized for PseuServer and fun :) It's written in pure
Python and has no external dependencies. The target are small apps or 
fake api that would be blown away by a SQL-DB or an external database server.

Many thanks to :
================

Markus Siemens's TinyDB. All credit should go to Markus, upon his hard work
I can create the PseuDB as what I want. I borrow some concepts from lowdb which 
will have better support for Restful API. 

Difference between TinyDB and PseuDB

- **No default table** The _default table has been removed from PseuDB. User needs to create a table first before inserting any data. 

- **Built-in ID** PseuDB always attachs a built-in id field, to every record, but user can customize the built-in id field as they prefer. 

- **Only table object can execute CRUD** The instance of TinyDB can execute CRUD actions, but it is different story in PseuDB. In PseuDB only the instance of table is allowed to execute CRUD actions. This concept is borrowed from lowdb. 

- **Return object instead of ID** PseuDB will return new or updated objects with IDs after the data is inserted or updated. It is good for Restful API to present the latest data in the database. 

- **Format of database is not compatible** Database file created by TinyDB will not be compatible with PseuDB, because data structure stored as list in PseuDB instead of dict in TinyDB. 


Installation
************

- Via pypi

.. code-block:: bash

    $ pip install pseudb

- Via github

.. code-block:: bash

    $ pip install -e git+https://github.com/harryho/pseudb@master#egg=pseudb


Example code
************

- Create database file with empty table1

.. code-block:: python

    >>> from pseudb import PseuDB, where
    >>> from pseudb.storages import JSONStorage
    >>> db = PseuDB('/path/to/db.json', storage=JSONStorage)
    >>> db.table('table1') # Method table will create or retrieve if it exists
    >>> db.get('table1')  # Method get only retrieve the table it exists

- Insert or update data into table1

.. code-block:: python

    >>> db.table('table1').insert({'data':1 })
    >>> db.get('table1').insert({'data':2 })
    >>> tb = db.get('table1')
    >>> tb.all()
    >>> tb.update({'data': 100}, where('data') ==1 )
    >>> tb.all()


- Query data from table1

.. code-block:: python

    >>> tb = db.get('table1')
    >>> tb.search(Query().data == 2)

- Customize default unique id field `id`

.. code-block:: python

    >>> tb2 = db.table('table2' , id_field = '_guid')
    >>> tb2.insert({'data':1 })
    >>> tb2.all()


Stable release
**************

- |PseuDB 3.1.0|


Old versions
************

- |PseuDB 2.0.0|

- |PseuDB 1.1.0|


Change log
**********

- PseuDB 3.1.0

    Change the get method 

- PseuDB 3.0.0 

    Change the built-in field from '_oid' to 'id'.

- PseuDB 2.1.0

    Change the insert and update method to return new or updated objects.



.. |Build Status| image:: https://travis-ci.org/harryho/pseudb.svg?branch=master
    :target: https://travis-ci.org/harryho/pseudb
.. |Coverage| image:: https://coveralls.io/repos/github/harryho/pseudb/badge.svg?branch=master
    :target: https://coveralls.io/github/harryho/pseudb?branch=master
.. |Version| image:: https://badge.fury.io/py/pseudb.svg
    :target: https://badge.fury.io/py/pseudb
.. _TinyDB: https://github.com/msiemens/tinydb
.. _lowdb: https://github.com/typicode/lowdb
.. |PseuDB 1.1.0| :target:: https://pypi.python.org/pypi?:action=display&name=pseudb&version=1.1.0
.. |PseuDB 2.0.0| :target:: https://pypi.python.org/pypi?:action=display&name=pseudb&version=2.0.0
.. |PseuDB 2.1.0| :target:: https://pypi.python.org/pypi?:action=display&name=pseudb&version=2.1.0 