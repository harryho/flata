Flata
----

|Build Status| |Coverage| |Version|


Flata is inspired by TinyDB_ and lowdb_. It is a lightweight document 
oriented database optimized for FlatApi and fun :) It's written in pure
Python and has no external dependencies. The target are small apps or 
fake api that would be blown away by a SQL-DB or an external database server.

Many thanks to :
================

Markus Siemens's TinyDB. All credit should go to Markus, upon his hard work
I can create the Flata as what I want. I borrow some concepts from lowdb which 
will have better support for Restful API. 

Difference between TinyDB and Flata

- **No default table** The _default table has been removed from Flata. User needs to create a table first before inserting any data. 

- **Built-in ID** Flata always attachs a built-in id field, to every record, but user can customize the built-in id field as they prefer. 

- **Only table object can execute CRUD** The instance of TinyDB can execute CRUD actions, but it is different story in Flata. In Flata only the instance of table is allowed to execute CRUD actions. This concept is borrowed from lowdb. 

- **Return object instead of ID** Flata will return new or updated objects with IDs after the data is inserted or updated. It is good for Restful API to present the latest data in the database. 

- **Format of database is not compatible** Database file created by TinyDB will not be compatible with Flata, because data structure stored as list in Flata instead of dict in TinyDB. 


Installation
************

- Via pypi

.. code-block:: bash

    $ pip install flata

- Via github

.. code-block:: bash

    $ pip install -e git+https://github.com/harryho/flata@master#egg=flata


Example code
************

- Create database file with empty table1

.. code-block:: python

    >>> from flata import Flata, where
    >>> from flata.storages import JSONStorage
    >>> db = Flata('/path/to/db.json', storage=JSONStorage)
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
- |Flata 4.0.0|



Old versions
************
- |Flata 3.3.1|
- |Flata 3.2.0|



Change log
**********

- Flata 3.2.0

    Add ignore case feature for search and match methods

- Flata 3.1.0

    Change the get method 

- Flata 3.0.0 

    Change the built-in field from '_oid' to 'id'.



.. |Build Status| image:: https://travis-ci.org/harryho/flata.svg?branch=master
    :target: https://travis-ci.org/harryho/flata
.. |Coverage| image:: https://coveralls.io/repos/github/harryho/flata/badge.svg?branch=master
    :target: https://coveralls.io/github/harryho/flata?branch=master
.. |Version| image:: https://badge.fury.io/py/flata.svg
    :target: https://badge.fury.io/py/flata
.. _TinyDB: https://github.com/msiemens/tinydb
.. _lowdb: https://github.com/typicode/lowdb

.. |Flata 1.1.0| :target:: https://pypi.python.org/pypi?:action=display&name=flata&version=1.1.0
.. |Flata 2.0.0| :target:: https://pypi.python.org/pypi?:action=display&name=flata&version=2.0.0
.. |Flata 2.1.0| :target:: https://pypi.python.org/pypi?:action=display&name=flata&version=3.1.0 
.. |Flata 3.2.0| :target:: https://pypi.python.org/pypi?:action=display&name=flata&version=3.2.0 
.. |Flata 3.3.1| :target:: https://pypi.python.org/pypi?:action=display&name=flata&version=3.3.1
.. |Flata 4.0.0| :target:: https://pypi.python.org/pypi?:action=display&name=flata&version=4.0.0
